import os
import subprocess
import time
import logging
import tempfile
from typing import List, Optional, Dict, Any
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BrowserManager:
    def __init__(self):
        self.browsers: Dict[str, Browser] = {}
        self.contexts: Dict[str, BrowserContext] = {}
        self.pages: Dict[str, Page] = {}
        self.playwright = None
        self.temp_dirs: Dict[str, str] = {}
    
    def start_playwright(self):
        """启动Playwright"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        return self.playwright
    
    def open_browser_with_debug(self, browser_type: str, debug_port: int = 9222) -> bool:
        """
        打开带远程调试模式的浏览器
        
        Args:
            browser_type: 浏览器类型 (chrome, edge, firefox)
            debug_port: 远程调试端口
            
        Returns:
            是否成功打开
        """
        try:
            playwright = self.start_playwright()
            
            # 使用临时目录
            temp_dir = tempfile.mkdtemp(prefix="browser_profile_")
            
            launch_options = {
                "headless": False,
                "args": [
                    f"--remote-debugging-port={debug_port}",
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-extensions",
                    "--disable-gpu"
                ]
            }
            
            if browser_type.lower() == "chrome":
                browser = playwright.chromium.launch_persistent_context(
                    temp_dir,
                    **launch_options
                )
                browser_type_name = "chrome"
            elif browser_type.lower() == "edge":
                browser = playwright.chromium.launch_persistent_context(
                    temp_dir,
                    channel="msedge",
                    **launch_options
                )
                browser_type_name = "edge"
            elif browser_type.lower() == "firefox":
                browser = playwright.firefox.launch_persistent_context(
                    temp_dir,
                    **launch_options
                )
                browser_type_name = "firefox"
            else:
                logger.error(f"不支持的浏览器类型: {browser_type}")
                return False
            
            self.contexts["default"] = browser
            self.temp_dirs["default"] = temp_dir
            
            logger.info(f"已启动{browser_type_name}浏览器，调试端口: {debug_port}，配置目录: {temp_dir}")
            
            time.sleep(3)
            return True
        except Exception as e:
            logger.error(f"启动浏览器失败: {e}")
            return False
    
    def connect_to_browser(self, browser_type: str, debug_port: int = 9222, instance_id: str = "default") -> Optional[Browser]:
        """
        连接到浏览器（现在直接使用已启动的上下文）
        
        Args:
            browser_type: 浏览器类型 (chrome, edge, firefox)
            debug_port: 远程调试端口
            instance_id: 实例ID，用于区分多个浏览器实例
            
        Returns:
            浏览器实例，如果连接失败则返回None
        """
        try:
            if instance_id in self.contexts:
                context = self.contexts[instance_id]
                logger.info(f"使用已启动的{browser_type}浏览器实例 {instance_id}")
                return None  # 返回上下文已存在，无需再连接
            else:
                logger.error(f"浏览器实例 {instance_id} 不存在，请先启动浏览器")
                return None
        except Exception as e:
            logger.error(f"连接浏览器失败: {e}")
            return None
    
    def get_or_create_page(self, instance_id: str = "default") -> Optional[Page]:
        """
        获取或创建页面
        
        Args:
            instance_id: 浏览器实例ID
            
        Returns:
            页面实例，如果获取失败则返回None
        """
        if instance_id not in self.contexts:
            logger.error(f"浏览器实例 {instance_id} 不存在")
            return None
        
        if instance_id in self.pages:
            return self.pages[instance_id]
        
        try:
            context = self.contexts[instance_id]
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = context.new_page()
            
            self.pages[instance_id] = page
            logger.info(f"为实例 {instance_id} 获取/创建新页面")
            return page
        except Exception as e:
            logger.error(f"创建页面失败: {e}")
            return None
    
    def close_browser(self, instance_id: str = "default"):
        """
        关闭浏览器实例
        
        Args:
            instance_id: 浏览器实例ID
        """
        if instance_id in self.pages:
            try:
                del self.pages[instance_id]
            except Exception as e:
                logger.error(f"关闭页面失败: {e}")
        
        if instance_id in self.contexts:
            try:
                self.contexts[instance_id].close()
                del self.contexts[instance_id]
                logger.info(f"已关闭浏览器实例 {instance_id}")
            except Exception as e:
                logger.error(f"关闭浏览器失败: {e}")
    
    def close_all(self):
        """关闭所有浏览器实例"""
        for instance_id in list(self.contexts.keys()):
            self.close_browser(instance_id)
        
        if self.playwright:
            try:
                self.playwright.stop()
                self.playwright = None
                logger.info("已停止Playwright")
            except Exception as e:
                logger.error(f"停止Playwright失败: {e}")
    
    def check_connection(self, instance_id: str = "default") -> bool:
        """
        检查浏览器连接状态
        
        Args:
            instance_id: 浏览器实例ID
            
        Returns:
            连接状态
        """
        return instance_id in self.contexts
    
    def _get_browser_path_from_registry(self, browser_type: str) -> str:
        """
        从Windows注册表中获取浏览器路径
        
        Args:
            browser_type: 浏览器类型
            
        Returns:
            浏览器可执行文件路径，如果未找到则返回空字符串
        """
        try:
            import winreg
            
            if browser_type.lower() == "chrome":
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
                    r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
                ]
            elif browser_type.lower() == "edge":
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
                    r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"
                ]
            elif browser_type.lower() == "firefox":
                reg_paths = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
                    r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe"
                ]
            else:
                return ""
            
            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                    path, _ = winreg.QueryValueEx(key, "")
                    winreg.CloseKey(key)
                    if os.path.exists(path):
                        return path
                except:
                    pass
            
            return ""
        except Exception as e:
            logger.debug(f"从注册表获取浏览器路径失败: {e}")
            return ""
    
    def _get_browser_path_from_path(self, browser_type: str) -> str:
        """
        从环境变量PATH中获取浏览器路径
        
        Args:
            browser_type: 浏览器类型
            
        Returns:
            浏览器可执行文件路径，如果未找到则返回空字符串
        """
        try:
            import shutil
            
            if browser_type.lower() == "chrome":
                exe_name = "chrome.exe" if os.name == "nt" else "google-chrome"
            elif browser_type.lower() == "edge":
                exe_name = "msedge.exe" if os.name == "nt" else "microsoft-edge"
            elif browser_type.lower() == "firefox":
                exe_name = "firefox.exe" if os.name == "nt" else "firefox"
            else:
                return ""
            
            path = shutil.which(exe_name)
            if path and os.path.exists(path):
                return path
            
            if browser_type.lower() == "chrome" and os.name != "nt":
                path = shutil.which("chromium")
                if path and os.path.exists(path):
                    return path
            elif browser_type.lower() == "edge" and os.name != "nt":
                path = shutil.which("edge")
                if path and os.path.exists(path):
                    return path
            
            return ""
        except Exception as e:
            logger.debug(f"从PATH获取浏览器路径失败: {e}")
            return ""

# 全局浏览器管理器实例
browser_manager = BrowserManager()

if __name__ == "__main__":
    manager = BrowserManager()
    
    try:
        print("测试浏览器启动...")
        success = manager.open_browser_with_debug("chrome", 9222)
        
        if success:
            print("浏览器启动成功！")
            
            print("测试页面创建页面...")
            page = manager.get_or_create_page("default")
            
            if page:
                print("页面创建成功！")
                print("导航到 Google...")
                page.goto("https://www.google.com")
                print("导航成功！")
                time.sleep(5)
                
                print("关闭浏览器...")
                manager.close_browser("default")
                print("浏览器已关闭！")
        
        manager.close_all()
        print("测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        manager.close_all()
