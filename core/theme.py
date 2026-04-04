"""
Theme Manager - Mengelola tema aplikasi
"""

import flet as ft
import base64
import io
from PIL import Image
import colorsys
import requests

class BatikTheme:
    # Default colors
    PRIMARY = "#7B3F00"  # Coklat batik
    SECONDARY = "#B87333"  # Copper
    ACCENT = "#D4AF37"  # Gold
    SUCCESS = "#2E7D32"
    ERROR = "#C62828"
    WARNING = "#ED6C02"
    INFO = "#2196F3"
    
    # Background colors
    BG_PRIMARY = "#FDF8F0"  # Off-white
    BG_SECONDARY = "#F5EDE3"
    BG_CARD = "#FFFFFF"
    
    # Text colors
    TEXT_PRIMARY = "#2C1810"
    TEXT_SECONDARY = "#5C3E2D"
    TEXT_HINT = "#9B7B5C"
    TEXT_WHITE = "#FFFFFF"
    TEXT_DARK = "#1A1A1A"
    
    # Border
    DIVIDER = "#E5D5BC"
    BORDER = "#D4B68A"
    
    # Badge colors
    BADGE_HALAL = "#2E7D32"
    BADGE_ECO = "#2E7D32"
    BADGE_PREMIUM = "#C62828"
    BADGE_PREORDER = "#FF9800"
    BADGE_SPECIAL = "#9C27B0"
    BADGE_READY = "#2E7D32"
    BADGE_HABIS = "#C62828"
    
    # Gradients
    GRADIENT_PRIMARY = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=["#7B3F00", "#5C2D00"]
    )
    GRADIENT_INDIGO = ft.LinearGradient(
        begin=ft.Alignment(-1, -1),
        end=ft.Alignment(1, 1),
        colors=["#3F2B1D", "#5C3E2D"]
    )
    
    # Shadows
    SHADOW_SM = ft.BoxShadow(
        blur_radius=4,
        color=ft.Colors.with_opacity(0.1, "#000000"),
        offset=ft.Offset(0, 2),
    )
    SHADOW_MD = ft.BoxShadow(
        blur_radius=8,
        color=ft.Colors.with_opacity(0.15, "#000000"),
        offset=ft.Offset(0, 4),
    )
    
    # Border radius
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_FULL = 999
    
    # Font sizes
    FONT_XS = 11
    FONT_SM = 13
    FONT_MD = 15
    FONT_LG = 18
    FONT_XL = 24
    
    # Spacing
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 12
    SPACE_LG = 16
    SPACE_XL = 24
    
    @classmethod
    def update_from_image(cls, image_data: bytes):
        """Update theme colors from uploaded image data"""
        try:
            img = Image.open(io.BytesIO(image_data))
            img = img.convert('RGB')
            return cls._update_from_pil_image(img)
        except Exception as e:
            print(f"[Theme] Error updating from image data: {e}")
            return False
    
    @classmethod
    def update_from_url(cls, url: str):
        """Update theme colors from image URL"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                img = img.convert('RGB')
                return cls._update_from_pil_image(img)
        except Exception as e:
            print(f"[Theme] Error updating from URL: {e}")
        return False
    
    @classmethod
    def _update_from_pil_image(cls, img):
        """Update theme from PIL Image with improved color extraction"""
        try:
            # Get dominant colors with better saturation
            colors = cls._get_dominant_colors_improved(img, 8)
            
            if colors:
                # Find a color with good saturation (not too light/white)
                primary = None
                for color in colors:
                    r, g, b = color
                    # Calculate luminance and saturation
                    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                    saturation = cls._calculate_saturation(r, g, b)
                    # Skip very light colors (white/cream) and very dark colors
                    if 0.2 < luminance < 0.85 and saturation > 0.15:
                        primary = color
                        break
                
                # If no good color found, use the first non-light color
                if not primary:
                    for color in colors:
                        r, g, b = color
                        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                        if luminance < 0.85:  # Not too light
                            primary = color
                            break
                
                # Default to first color if still none
                if not primary:
                    primary = colors[0]
                
                # Set primary color (darken if needed)
                cls.PRIMARY = cls._darken_color_rgb(primary, 0.2)
                
                # Secondary from second dominant color (prefer darker)
                secondary = None
                if len(colors) > 1:
                    for color in colors[1:]:
                        luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
                        if luminance < 0.7:
                            secondary = color
                            break
                    if not secondary:
                        secondary = colors[1]
                    cls.SECONDARY = cls._rgb_to_hex(secondary)
                
                # Accent - complementary color with better contrast
                r, g, b = primary
                h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
                # Use complementary color (opposite on color wheel)
                accent_h = (h + 0.5) % 1.0
                # Increase saturation for better visibility
                accent_s = min(1.0, s * 1.3)
                accent_v = min(1.0, v * 1.1)
                accent_rgb = colorsys.hsv_to_rgb(accent_h, accent_s, accent_v)
                cls.ACCENT = cls._rgb_to_hex([int(c * 255) for c in accent_rgb])
                
                # Set background color (light cream/off-white with slight tint)
                r, g, b = primary
                bg_r = min(255, int(r * 0.85 + 100))
                bg_g = min(255, int(g * 0.85 + 90))
                bg_b = min(255, int(b * 0.85 + 80))
                cls.BG_PRIMARY = cls._rgb_to_hex((bg_r, bg_g, bg_b))
                
                # Card background (slightly lighter)
                card_r = min(255, bg_r + 20)
                card_g = min(255, bg_g + 20)
                card_b = min(255, bg_b + 20)
                cls.BG_CARD = cls._rgb_to_hex((card_r, card_g, card_b))
                
                # Text color based on luminance
                luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                if luminance > 0.5:
                    cls.TEXT_PRIMARY = "#2C1810"  # Dark text for light backgrounds
                    cls.TEXT_SECONDARY = "#5C3E2D"
                else:
                    cls.TEXT_PRIMARY = "#FFFFFF"  # Light text for dark backgrounds
                    cls.TEXT_SECONDARY = "#E0E0E0"
                
                # Update gradient
                cls.GRADIENT_PRIMARY = ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[cls.PRIMARY, cls._darken_color_rgb(primary, 0.3)]
                )
                
                return True
        except Exception as e:
            print(f"[Theme] Error processing image: {e}")
        
        return False
    
    @classmethod
    def _calculate_saturation(cls, r, g, b):
        """Calculate saturation of RGB color"""
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        if max_val == 0:
            return 0
        return (max_val - min_val) / max_val
    
    @classmethod
    def _get_dominant_colors_improved(cls, img, num_colors=8):
        """Extract dominant colors with better quality"""
        # Resize image for faster processing
        img.thumbnail((150, 150))
        
        # Get colors with frequency
        colors = img.getcolors(img.size[0] * img.size[1])
        if not colors:
            return None
        
        # Filter out near-white colors (luminance > 0.95)
        filtered_colors = []
        for count, color in colors:
            luminance = (0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]) / 255
            if luminance < 0.92:  # Skip very light colors
                filtered_colors.append((count, color))
        
        # Sort by count
        filtered_colors.sort(key=lambda x: x[0], reverse=True)
        
        result = []
        for count, color in filtered_colors[:num_colors]:
            result.append(color)
        
        return result
    
    @classmethod
    def _get_dominant_colors(cls, img, num_colors=5):
        """Original method - kept for compatibility"""
        img.thumbnail((100, 100))
        
        colors = img.getcolors(img.size[0] * img.size[1])
        if not colors:
            return None
        
        colors.sort(key=lambda x: x[0], reverse=True)
        
        result = []
        for count, color in colors[:num_colors]:
            result.append(color)
        
        return result
    
    @classmethod
    def _rgb_to_hex(cls, rgb):
        """Convert RGB tuple to hex color"""
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    @classmethod
    def _darken_color_rgb(cls, rgb, factor):
        """Darken RGB color by factor"""
        return cls._rgb_to_hex([int(c * (1 - factor)) for c in rgb])
    
    @classmethod
    def _darken_color(cls, rgb, factor):
        """Darken RGB color"""
        return cls._rgb_to_hex([int(c * (1 - factor)) for c in rgb])
    
    @classmethod
    def set_manual_colors(cls, primary, secondary, accent, bg_primary, bg_card):
        """Manually set theme colors"""
        cls.PRIMARY = primary
        cls.SECONDARY = secondary
        cls.ACCENT = accent
        cls.BG_PRIMARY = bg_primary
        cls.BG_CARD = bg_card
        
        # Update gradient
        cls.GRADIENT_PRIMARY = ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[cls.PRIMARY, cls._darken_color_rgb(cls._hex_to_rgb(primary), 0.2)]
        )
        
        # Update text color based on background
        r, g, b = cls._hex_to_rgb(bg_primary)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        if luminance > 0.5:
            cls.TEXT_PRIMARY = "#2C1810"
            cls.TEXT_SECONDARY = "#5C3E2D"
        else:
            cls.TEXT_PRIMARY = "#FFFFFF"
            cls.TEXT_SECONDARY = "#E0E0E0"
    
    @classmethod
    def _hex_to_rgb(cls, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @classmethod
    def get_theme(cls):
        """Get Flet theme object"""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=cls.PRIMARY,
                secondary=cls.SECONDARY,
                surface=cls.BG_CARD,
                error=cls.ERROR,
            ),
            visual_density=ft.VisualDensity.ADAPTIVE_PLATFORM_DENSITY,
        )