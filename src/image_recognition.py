"""
图像识别模块
用于识别游戏界面状态和元素
"""
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple, List, Dict
from pathlib import Path
from enum import Enum, auto
import time


class GameState(Enum):
    """游戏状态枚举"""
    UNKNOWN = auto()           # 未知状态
    LEVEL_PREPARE = auto()     # 关卡准备界面（图1）
    CARD_SELECTION = auto()    # 卡牌选择界面（图2）
    OBSTACLE_CONTINUE = auto() # 障碍物界面-继续按钮（图3）
    OBSTACLE_CHOICE = auto()   # 障碍物界面-三选一（图4）
    VICTORY = auto()           # 胜利界面（图5）
    DEFEAT = auto()            # 失败界面
    PURCHASE_FAILED = auto()   # 购买失败界面
    PURCHASE = auto()          # 购买界面 (图7)
    LEVEL_UP = auto()          # 升级界面 (图4)
    LEVEL_UP_AFTER = auto()    # 升级后界面 (图8, 需关闭)
    OBSTACLE_SPECIALBOX = auto() # 特殊障碍物宝箱界面


class ImageRecognizer:
    """图像识别器"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        初始化图像识别器
        
        Args:
            templates_dir: 模板图片目录
        """
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, np.ndarray] = {}
        
        # 初始化 SIFT 算法及特殊特征缓存
        self.sift = cv2.SIFT_create()
        self._special_box_kp = None
        self._special_box_des = None
        self._retry_banner_kp = None
        self._retry_banner_des = None
        
        self._load_templates()
        self._prepare_special_features()
    
    def _load_templates(self):
        """递归加载模板图片"""
        if not self.templates_dir.exists():
            print(f"警告: 模板目录不存在: {self.templates_dir}")
            return
        
        # 递归加载所有PNG模板（包括子目录，如ui/）
        for template_file in self.templates_dir.rglob("*.png"):
            name = template_file.stem
            img = cv2.imread(str(template_file), cv2.IMREAD_COLOR)
            if img is not None:
                self.templates[name] = img
                print(f"已加载模板: {name} (路径: {template_file.relative_to(self.templates_dir)})")
    
    def _prepare_special_features(self):
        """预计算特殊 UI 元素的特征点，提高识别鲁棒性"""
        if "btn_specialbox_circle" in self.templates:
            tpl = self.templates["btn_specialbox_circle"]
            # 预先提取特征点和描述符
            self._special_box_kp, self._special_box_des = self.sift.detectAndCompute(tpl, None)
            print(f"✅ 已预计算特殊宝箱特征点: {len(self._special_box_kp) if self._special_box_kp else 0} 个")
            
        if "btn_retry_banner" in self.templates:
            tpl = self.templates["btn_retry_banner"]
            self._retry_banner_kp, self._retry_banner_des = self.sift.detectAndCompute(tpl, None)
            print(f"✅ 已预计算重投按钮特征点: {len(self._retry_banner_kp) if self._retry_banner_kp else 0} 个")
    
    def pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """PIL图像转OpenCV格式"""
        # 转换为RGB（PIL默认是RGB）
        rgb = np.array(pil_image)
        # OpenCV使用BGR
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        return bgr
    
    def find_template(
        self,
        screen: np.ndarray,
        template_name: str,
        threshold: float = 0.8
    ) -> Optional[Tuple[int, int, float]]:
        """
        在屏幕中查找模板
        
        Args:
            screen: 屏幕截图（OpenCV格式）
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            (x, y, confidence) 匹配位置和置信度，未找到返回None
        """
        if template_name not in self.templates:
            return None
        
        template = self.templates[template_name]
        
        # 模板匹配
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            # 返回模板中心位置
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y, max_val)
        
        return None
    
    def find_all_templates(
        self,
        screen: np.ndarray,
        template_name: str,
        threshold: float = 0.8
    ) -> List[Tuple[int, int, float]]:
        """
        在屏幕中查找所有匹配的模板
        
        Args:
            screen: 屏幕截图
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            [(x, y, confidence), ...] 所有匹配位置列表
        """
        if template_name not in self.templates:
            return []
        
        template = self.templates[template_name]
        h, w = template.shape[:2]
        
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        matches = []
        for pt in zip(*locations[::-1]):  # 转换为(x, y)格式
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            confidence = result[pt[1], pt[0]]
            matches.append((center_x, center_y, confidence))
        
        # 去除重叠的匹配（NMS）
        return self._non_max_suppression(matches, w, h)
    
    def _non_max_suppression(
        self,
        matches: List[Tuple[int, int, float]],
        width: int,
        height: int
    ) -> List[Tuple[int, int, float]]:
        """非极大值抑制，去除重叠匹配"""
        if not matches:
            return []
        
        # 按置信度排序
        matches = sorted(matches, key=lambda x: x[2], reverse=True)
        
        result = []
        for match in matches:
            x, y, conf = match
            # 检查是否与已有结果重叠
            overlap = False
            for rx, ry, _ in result:
                if abs(x - rx) < width * 0.5 and abs(y - ry) < height * 0.5:
                    overlap = True
                    break
            
            if not overlap:
                result.append(match)
        
        return result
    
    def detect_state(self, screen: np.ndarray) -> GameState:
        """
        检测当前游戏状态
        
        Args:
            screen: 屏幕截图（OpenCV格式）
            
        Returns:
            当前游戏状态
        """
        h_img, w_img = screen.shape[:2]
        hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
        h, w = h_img, w_img

        # ===== 0. 预先计算通用全局特征 (用于各状态判定和互斥校验) =====
        
        # 底部橙色像素
        orange_mask_full = cv2.inRange(hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
        bottom_region_orange = orange_mask_full[int(h*0.7):, :]
        bottom_orange_pixels = cv2.countNonZero(bottom_region_orange)

        # 卡牌描述区域的米色背景 (关键特征：识别卡牌界面)
        description_region = hsv[int(h*0.5):int(h*0.75), int(w*0.1):int(w*0.9)]
        beige_mask = cv2.inRange(description_region, np.array([15, 5, 180]), np.array([35, 80, 255]))
        beige_pixels = cv2.countNonZero(beige_mask)
        
        # 左下角属性面板 (暗色背景)
        bottom_left_panel = screen[int(h*0.5):, :int(w*0.25)]
        bl_hsv = cv2.cvtColor(bottom_left_panel, cv2.COLOR_BGR2HSV)
        dark_mask = cv2.inRange(bl_hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
        dark_pixels = cv2.countNonZero(dark_mask)

        # 顶部 UI 区域的金色与银色 (游戏主界面的核心特征)
        top_region_hsv = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
        gold_mask = cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
        gold_pixels = cv2.countNonZero(gold_mask)
        silver_mask = cv2.inRange(top_region_hsv, np.array([0, 0, 150]), np.array([180, 50, 255]))
        silver_pixels = cv2.countNonZero(silver_mask)

        # ===== 1. 特别检测：特殊障碍物宝箱界面 (SIFT 特征匹配法 - 终极方案) =====
        # 该界面背景多变（大漠、森林等），光影动画复杂，且局部可能被干扰。
        # SIFT 具有尺度、旋转和光照不变性，是解决此类问题的最有效手段。
        if self._special_box_des is not None:
            # 限制区域在中心 [250:650, 600:1000]，减少计算并排除边角干扰
            roi = screen[250:650, 600:1000]
            kp_scene, des_scene = self.sift.detectAndCompute(roi, None)
            
            if des_scene is not None:
                # 使用 FLANN 或 BF 匹配
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(self._special_box_des, des_scene, k=2)
                
                # Lowe's Ratio Test 过滤噪声 (核心步骤)
                good_matches = []
                for match_pair in matches:
                    if len(match_pair) == 2:
                        m, n = match_pair
                        if m.distance < 0.7 * n.distance:
                            good_matches.append(m)
                
                # 统计有效匹配点数量
                # 根据测试：空界面或战斗干扰 < 10 个，真实宝箱界面 > 100 个
                # 设置阈值 30 是极度安全且稳健的
                if len(good_matches) >= 30:
                    # 只有在初次检测到时才打印详细日志，避免刷屏
                    return GameState.OBSTACLE_SPECIALBOX

        # ===== 2. 检测购买失败界面（阻塞性弹窗） =====
        # 注意：购买失败弹窗会遮挡住背景，导致顶部 UI 的金色特征消失或大幅减弱。
        # 如果检测到大量金色/银色像素，优先排除弹窗状态。
        if gold_pixels < 5000:
            center_text_region = screen[int(h*0.35):int(h*0.55), int(w*0.3):int(w*0.7)]
            center_gray = cv2.cvtColor(center_text_region, cv2.COLOR_BGR2GRAY)
            white_text_pixels = cv2.countNonZero((center_gray > 200).astype(np.uint8))
            dark_bg_pixels = cv2.countNonZero((center_gray < 80).astype(np.uint8))
            
            button_check_region = hsv[int(h*0.55):int(h*0.75), int(w*0.35):int(w*0.65)]
            orange_mask = cv2.inRange(button_check_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
            button_orange_pixels = cv2.countNonZero(orange_mask)
            
            # 初步像素特征判断
            if white_text_pixels > 2000 and dark_bg_pixels > 20000 and button_orange_pixels > 5000:
                pf_x, pf_y = 800, 640
                pf_rect = hsv[pf_y-30:pf_y+30, pf_x-100:pf_x+100]
                pf_orange_mask = cv2.inRange(pf_rect, np.array([10, 120, 120]), np.array([25, 255, 255]))
                pf_density = cv2.countNonZero(pf_orange_mask) / (pf_rect.size/3)
                
                if 0.5 < pf_density < 0.9:
                    # 像素特征符合，使用模板匹配进行二次确认（提高鲁棒性）
                    if self.find_template(screen, "purchase_failed", threshold=0.6):
                        return GameState.PURCHASE_FAILED
                    else:
                        # 如果没有找到模板，但在调试日志中看到频繁触发，可能需要记录
                        pass

        # 0. 检测卡牌选择界面 (特征：SIFT 匹配右下角“重投”按钮 OR 大量米色描述背景)
        # 该界面在特殊情况下（如开场秒杀升级）会被大幅压暗，导致所有颜色特征失效。
        # 唯有右下角的“重投”按钮结构稳定，使用 SIFT 特征匹配是唯一稳健方案。
        
        # A. SIFT 结构匹配 (核心方案：适配所有光影和稀有度)
        if self._retry_banner_des is not None:
            # 限制在右下角区域 [700:, 1100:] 以提高速度并减少干扰
            retry_roi = screen[700:, 1100:]
            if retry_roi.size == 0 or retry_roi.shape[0] < 10 or retry_roi.shape[1] < 10:
                kp_r, des_r = None, None
            else:
                kp_r, des_r = self.sift.detectAndCompute(retry_roi, None)
            
            if des_r is not None:
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(self._retry_banner_des, des_r, k=2)
                good_retry = []
                for m_pair in matches:
                    if len(m_pair) == 2:
                        m, n = m_pair
                        if m.distance < 0.7 * n.distance:
                            good_retry.append(m)
                
                # 经过实测：真实界面匹配点 > 40，其他界面 < 10
                if len(good_retry) >= 30:
                    return GameState.CARD_SELECTION

        # B. 标准模式兜底：米色描述背景
        if beige_pixels > 50000:
            top_left_region = hsv[:int(h*0.3), :int(w*0.3)]
            english_btn_mask_orange = cv2.inRange(top_left_region, np.array([10, 100, 100]), np.array([25, 255, 255]))
            english_pixels = cv2.countNonZero(english_btn_mask_orange)
            
            bottom_right_region = hsv[int(h*0.7):, int(w*0.7):]
            retry_btn_mask = cv2.inRange(bottom_right_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
            retry_pixels = cv2.countNonZero(retry_btn_mask)
            
            if (english_pixels > 5000 or retry_pixels > 5000) and english_pixels < 50000:
                return GameState.CARD_SELECTION
            if dark_pixels > 80000:
                return GameState.CARD_SELECTION

        # 1. 检测胜利界面的绿色"胜利"横幅
        if bottom_orange_pixels > 3000:
            victory_region = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
            green_lower = np.array([35, 80, 80])
            green_upper = np.array([85, 255, 255])
            green_mask = cv2.inRange(victory_region, green_lower, green_upper)
            green_pixels = cv2.countNonZero(green_mask)
            
            # 只有当绿色足够多且没有大量米色背景时，才认为是胜利
            if green_pixels > 8000 and beige_pixels < 5000:
                return GameState.VICTORY
        
        # 2. 检测关卡准备界面的 "Best time" 区域 (特征非常稳定)
        # 左下角会有固定位置的深色矩形框 + "Best time" 白色文字
        best_time_region = screen[int(h*0.85):int(h*0.95), :int(w*0.15)]
        bt_gray = cv2.cvtColor(best_time_region, cv2.COLOR_BGR2GRAY)
        white_text = cv2.countNonZero((bt_gray > 200).astype(np.uint8))
        dark_bg = cv2.countNonZero((bt_gray < 60).astype(np.uint8))
        
        # Best time区域应该有显著的深色背景和白色文字对比，且绝对不能有米色背景（排除卡牌界面）
        is_level_prepare_feature = white_text > 150 and dark_bg > 300 and white_text < dark_bg and beige_pixels < 10000
        
        if is_level_prepare_feature:
            # A. 真正的关卡准备界面：有Start按钮 (底部中间黄色)
            start_btn_region = hsv[int(h*0.8):int(h*0.95), int(w*0.4):int(w*0.6)]
            start_btn_mask = cv2.inRange(start_btn_region, np.array([15, 100, 100]), np.array([40, 255, 255]))
            start_btn_pixels = cv2.countNonZero(start_btn_mask)
            
            if start_btn_pixels > 1000:
                return GameState.LEVEL_PREPARE
                
            # B. 升级后界面：有Close按钮 (右上角红色) 且无Start按钮
            # 按钮位置 [1520, 80], 检测区域 [1480:1560, 40:120]
            cancel_btn_region = hsv[40:120, 1480:1560]
            red_mask1 = cv2.inRange(cancel_btn_region, np.array([0, 100, 100]), np.array([10, 255, 255]))
            red_mask2 = cv2.inRange(cancel_btn_region, np.array([160, 100, 100]), np.array([180, 255, 255]))
            cancel_btn_pixels = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)
            
            if cancel_btn_pixels > 1000:
                return GameState.LEVEL_UP_AFTER

        # 3. 检测购买界面（弹窗，特征明显）
        # 特征：右上角有红色关闭按钮
        # 按钮位置 [1520, 80], 检测区域 [1480:1560, 40:120]
        cancel_btn_region = hsv[40:120, 1480:1560]
        red_mask1 = cv2.inRange(cancel_btn_region, np.array([0, 100, 100]), np.array([10, 255, 255]))
        red_mask2 = cv2.inRange(cancel_btn_region, np.array([160, 100, 100]), np.array([180, 255, 255]))
        cancel_btn_pixels = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)
        
        # 提高购买界面阈值，避免胜利界面误判 (709 -> 1200)
        # 并且要求没有Best Time特征（避免level_prepare误判）
        if cancel_btn_pixels > 1000 and not is_level_prepare_feature:
            return GameState.PURCHASE
        
        # 4. 检测升级界面 (特征：底部中间有橙色按钮 + 顶部有金色)
        if bottom_orange_pixels > 3000:
            # 检测区域 [740:820, 700:900]
            level_up_btn_region = hsv[740:820, 700:900]
            level_up_orange_mask = cv2.inRange(level_up_btn_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
            level_up_pixels = cv2.countNonZero(level_up_orange_mask)
            
            if level_up_pixels > 8000 and gold_pixels > 10000:
                return GameState.LEVEL_UP
                
        # 5. 检测障碍物三选一界面（顶部金色框是唯一特征）
        if dark_pixels > 5000 and gold_pixels > 15000 and silver_pixels > 5000 and bottom_orange_pixels < 30000:
            return GameState.OBSTACLE_CHOICE
            
        # 6. 最后兜底检测障碍物继续界面
        # 特征：右侧中心区域有明显的按钮 (橙色/红色系)
        btn_roi_hsv = hsv[int(h*0.3):int(h*0.6), int(w*0.8):]
        btn_mask = cv2.inRange(btn_roi_hsv, np.array([0, 100, 100]), np.array([25, 255, 255]))
        btn_pixels = cv2.countNonZero(btn_mask)
        
        # 辅助参考特征：右侧灰色/边缘
        right_gray_pixels = cv2.countNonZero(cv2.inRange(btn_roi_hsv, np.array([0, 0, 50]), np.array([180, 50, 200])))
        
        # 如果检测到右侧有明显的按钮特征
        # 备注：不再强依赖 gold_pixels > 80000，因为背景多变
        if btn_pixels > 2000 and (gold_pixels > 20000 or right_gray_pixels > 2000):
            return GameState.OBSTACLE_CONTINUE
            
        return GameState.UNKNOWN
    
    def detect_card_ids(
        self,
        screen: np.ndarray,
        card_positions: List[Tuple[int, int]],
        card_weights: dict
    ) -> List[Optional[str]]:
        """
        识别卡牌ID (通过极速模板匹配)
        
        Args:
            screen: 屏幕截图
            card_positions: 卡牌中心位置列表
            card_weights: 已知权重的ID列表 (用于优先匹配)
            
        Returns:
            卡牌ID(字符串)列表，无法识别的为None
        """
        results = []
        
        for i, (x, y) in enumerate(card_positions):
            # 截取ID区域 (根据1600x900适配)
            # ID在卡牌上方，适当扩大区域以确保模板能放入 (200x100 搜索框)
            left, top = x - 100, y - 460
            right, bottom = x + 100, y - 360
            
            # 环境适配
            left, top = max(0, left), max(0, top)
            right, bottom = min(screen.shape[1], right), min(screen.shape[0], bottom)
            
            id_region = screen[top:bottom, left:right]
            
            # 尝试在 templates/cards 目录中匹配已知 ID
            found_id = None
            max_val = 0
            
            # 获取所有卡牌 ID 模板
            card_template_dir = self.templates_dir / "cards"
            if not card_template_dir.exists():
                card_template_dir.mkdir(parents=True, exist_ok=True)
            
            for template_file in card_template_dir.glob("*.png"):
                id_name = template_file.stem
                templ = cv2.imread(str(template_file), cv2.IMREAD_COLOR)
                if templ is None: continue
                
                res = cv2.matchTemplate(id_region, templ, cv2.TM_CCOEFF_NORMED)
                _, val, _, _ = cv2.minMaxLoc(res)
                
                if val > 0.85 and val > max_val:
                    max_val = val
                    found_id = id_name
            
            if found_id:
                results.append(found_id)
            else:
                # 如果没找到，保存该区域以便用户以后手动添加模板
                debug_path = f"debug_unknown_card_{int(time.time())}_{i}.png"
                cv2.imwrite(debug_path, id_region)
                results.append(None)
                
        return results
    
    def get_card_positions(self, screen: np.ndarray) -> List[Tuple[int, int]]:
        """
        获取屏幕上所有卡牌的位置
        
        Args:
            screen: 屏幕截图
            
        Returns:
            卡牌中心位置列表
        """
        # 首先尝试通过模板匹配
        cards = self.find_all_templates(screen, "card_frame", 0.7)
        if cards:
            return [(x, y) for x, y, _ in cards]
        
        # 如果没有模板，使用固定位置（1600x900分辨率下的三张卡牌）
        # 根据图2，三张卡牌大致在屏幕中间均匀分布
        return [
            (320, 350),   # 左边卡牌
            (800, 350),   # 中间卡牌
            (1280, 350),  # 右边卡牌
        ]
    
    def get_choice_positions(self, screen: np.ndarray) -> List[Tuple[int, int]]:
        """
        获取屏幕上选项的位置
        
        Args:
            screen: 屏幕截图
            
        Returns:
            选项中心位置列表
        """
        # 首先尝试通过模板匹配
        choices = self.find_all_templates(screen, "choice_box", 0.7)
        if choices:
            # 按X坐标排序
            choices = sorted(choices, key=lambda x: x[0])
            return [(x, y) for x, y, _ in choices]
        
        # 使用固定位置（1600x900分辨率）
        # 根据图4，三个选项在屏幕上方均匀分布
        return [
            (530, 200),   # 左边选项
            (800, 200),   # 中间选项
            (1070, 200),  # 右边选项
        ]


# 测试代码
if __name__ == "__main__":
    recognizer = ImageRecognizer()
    
    # 加载测试图片
    test_image_path = "test_screenshot.png"
    try:
        img = cv2.imread(test_image_path)
        if img is not None:
            state = recognizer.detect_state(img)
            print(f"检测到的游戏状态: {state.name}")
        else:
            print(f"无法加载测试图片: {test_image_path}")
    except Exception as e:
        print(f"测试失败: {e}")
