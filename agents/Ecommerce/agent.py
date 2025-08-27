"""
E-commerce Agent with Google ADK
A sophisticated e-commerce assistant using Google's Agent Development Kit.
"""

from google.adk.agents import Agent
from google.genai import types
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from difflib import get_close_matches
import json
import logging

# -------------------------
# Configuration
# -------------------------

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
TAX_RATE = 0.08  # 8% tax
SHIPPING_THRESHOLD = 100  # Free shipping above this amount
SHIPPING_COST = 10  # Fixed shipping cost
DISCOUNT_CODES = {
    "WELCOME10": 0.10,  # 10% discount
    "SAVE20": 0.20,     # 20% discount
    "VIP30": 0.30       # 30% discount
}

# -------------------------
# Data Models
# -------------------------

@dataclass
class Product:
    """Product model with all relevant information."""
    id: str
    nombre: str
    precio: float
    stock: int
    características: List[str]
    categoria: str = "General"
    descripcion: str = ""
    rating: float = 0.0
    reviews: int = 0

@dataclass
class CartItem:
    """Cart item model."""
    producto_id: str
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float = field(init=False)
    
    def __post_init__(self):
        self.subtotal = self.precio_unitario * self.cantidad

@dataclass
class Cart:
    """Shopping cart model."""
    items: List[CartItem] = field(default_factory=list)
    discount_code: Optional[str] = None
    
    def get_subtotal(self) -> float:
        """Calculate cart subtotal."""
        return sum(item.subtotal for item in self.items)
    
    def get_discount_amount(self) -> float:
        """Calculate discount amount."""
        if self.discount_code and self.discount_code in DISCOUNT_CODES:
            return self.get_subtotal() * DISCOUNT_CODES[self.discount_code]
        return 0.0
    
    def get_tax(self) -> float:
        """Calculate tax amount."""
        subtotal_after_discount = self.get_subtotal() - self.get_discount_amount()
        return subtotal_after_discount * TAX_RATE
    
    def get_shipping(self) -> float:
        """Calculate shipping cost."""
        if self.get_subtotal() >= SHIPPING_THRESHOLD:
            return 0.0
        return SHIPPING_COST
    
    def get_total(self) -> float:
        """Calculate total amount."""
        subtotal = self.get_subtotal()
        discount = self.get_discount_amount()
        tax = self.get_tax()
        shipping = self.get_shipping()
        return subtotal - discount + tax + shipping

# -------------------------
# Enhanced Product Catalog
# -------------------------

PRODUCTOS_DB: Dict[str, Product] = {
    "laptop gamer pro": Product(
        id="LPG001",
        nombre="Laptop Gamer Pro",
        precio=1500,
        stock=10,
        características=["RTX 4070", "32GB RAM", "1TB SSD", "144Hz Display"],
        categoria="Computadoras",
        descripcion="Laptop gaming de alta gama para los juegos más exigentes",
        rating=4.8,
        reviews=127
    ),
    "teclado mecanico rgb": Product(
        id="TEC005",
        nombre="Teclado Mecánico RGB",
        precio=120,
        stock=25,
        características=["Switches Cherry MX", "RGB personalizable", "TKL", "USB-C"],
        categoria="Periféricos",
        descripcion="Teclado mecánico premium con iluminación RGB completa",
        rating=4.6,
        reviews=89
    ),
    "monitor 4k hdr": Product(
        id="MON003",
        nombre="Monitor 4K HDR",
        precio=400,
        stock=5,
        características=["27 pulgadas", "144Hz", "HDR10", "G-Sync Compatible"],
        categoria="Monitores",
        descripcion="Monitor gaming 4K con HDR para una experiencia visual inmersiva",
        rating=4.9,
        reviews=203
    ),
    "mouse gaming pro": Product(
        id="MOU002",
        nombre="Mouse Gaming Pro",
        precio=80,
        stock=15,
        características=["16000 DPI", "RGB", "8 botones programables", "Inalámbrico"],
        categoria="Periféricos",
        descripcion="Mouse gaming profesional con sensor de alta precisión",
        rating=4.7,
        reviews=156
    ),
    "auriculares 7.1": Product(
        id="AUR004",
        nombre="Auriculares Gaming 7.1",
        precio=150,
        stock=8,
        características=["Sonido 7.1 Surround", "Micrófono retráctil", "RGB", "Cancelación de ruido"],
        categoria="Audio",
        descripcion="Auriculares gaming con sonido envolvente para máxima inmersión",
        rating=4.5,
        reviews=94
    )
}

# -------------------------
# Shopping Cart State
# -------------------------

carrito = Cart()
historial_busquedas: List[str] = []

# -------------------------
# Helper Functions
# -------------------------

def find_product_fuzzy(nombre: str) -> Optional[Tuple[str, Product]]:
    """Find product using fuzzy matching."""
    nombre_lower = nombre.strip().lower()
    
    # Exact match
    if nombre_lower in PRODUCTOS_DB:
        return nombre_lower, PRODUCTOS_DB[nombre_lower]
    
    # Fuzzy match
    product_names = list(PRODUCTOS_DB.keys())
    matches = get_close_matches(nombre_lower, product_names, n=1, cutoff=0.6)
    
    if matches:
        match = matches[0]
        return match, PRODUCTOS_DB[match]
    
    return None

def format_price(amount: float) -> str:
    """Format price with currency."""
    return f"${amount:,.2f}"

def get_cart_item_by_product(producto_id: str) -> Optional[CartItem]:
    """Get cart item by product ID."""
    for item in carrito.items:
        if item.producto_id == producto_id:
            return item
    return None

# -------------------------
# Enhanced Tools
# -------------------------

def buscar_producto_por_nombre(nombre_producto: str) -> dict:
    """
    Busca un producto por nombre con búsqueda fuzzy y registra la búsqueda.
    
    Args:
        nombre_producto: Nombre del producto a buscar (búsqueda flexible).
        
    Returns:
        dict: Detalles completos del producto o sugerencias si no se encuentra.
    """
    logger.info(f"🔍 Buscando producto: '{nombre_producto}'")
    historial_busquedas.append(nombre_producto)
    
    result = find_product_fuzzy(nombre_producto)
    
    if result:
        key, producto = result
        return {
            "status": "success",
            "product": {
                "id": producto.id,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "precio_formateado": format_price(producto.precio),
                "stock": producto.stock,
                "características": producto.características,
                "categoria": producto.categoria,
                "descripcion": producto.descripcion,
                "rating": f"⭐ {producto.rating}/5.0 ({producto.reviews} reseñas)",
                "disponible": producto.stock > 0
            },
            "message": f"✅ Producto '{producto.nombre}' encontrado."
        }
    else:
        # Suggest similar products
        sugerencias = []
        for nombre in list(PRODUCTOS_DB.keys())[:3]:
            p = PRODUCTOS_DB[nombre]
            sugerencias.append(f"• {p.nombre} ({format_price(p.precio)})")
        
        return {
            "status": "not_found",
            "message": f"❌ No encontré '{nombre_producto}'.",
            "sugerencias": sugerencias,
            "sugerencias_text": "Productos disponibles:\n" + "\n".join(sugerencias)
        }

def agregar_al_carrito(producto: str, cantidad: int = 1) -> dict:
    """
    Agrega productos al carrito con validación completa y búsqueda inteligente.
    
    Args:
        producto: Nombre del producto (búsqueda flexible).
        cantidad: Cantidad a agregar (default: 1).
        
    Returns:
        dict: Confirmación con resumen del carrito actualizado.
    """
    logger.info(f"🛒 Agregando al carrito: {cantidad}x '{producto}'")
    
    # Validate quantity
    if not isinstance(cantidad, int) or cantidad <= 0:
        return {
            "status": "error",
            "message": "❌ La cantidad debe ser un número entero mayor que cero."
        }
    
    # Find product
    result = find_product_fuzzy(producto)
    if not result:
        return {
            "status": "error",
            "message": f"❌ No encontré el producto '{producto}'. Usa 'buscar_producto' para ver opciones."
        }
    
    key, product_info = result
    
    # Check if already in cart
    existing_item = get_cart_item_by_product(product_info.id)
    cantidad_actual = existing_item.cantidad if existing_item else 0
    
    # Verify stock
    if cantidad_actual + cantidad > product_info.stock:
        disponible = product_info.stock - cantidad_actual
        return {
            "status": "error",
            "message": f"❌ Stock insuficiente. Solo hay {disponible} unidades disponibles de '{product_info.nombre}'.",
            "stock_actual": product_info.stock,
            "en_carrito": cantidad_actual,
            "disponible": disponible
        }
    
    # Add to cart
    if existing_item:
        existing_item.cantidad += cantidad
        existing_item.subtotal = existing_item.precio_unitario * existing_item.cantidad
    else:
        carrito.items.append(CartItem(
            producto_id=product_info.id,
            nombre=product_info.nombre,
            precio_unitario=product_info.precio,
            cantidad=cantidad
        ))
    
    total_items = sum(item.cantidad for item in carrito.items)
    subtotal = carrito.get_subtotal()
    
    return {
        "status": "success",
        "message": f"✅ Agregado {cantidad}x '{product_info.nombre}' al carrito.",
        "producto_agregado": {
            "nombre": product_info.nombre,
            "cantidad": cantidad,
            "precio_unitario": format_price(product_info.precio),
            "subtotal": format_price(product_info.precio * cantidad)
        },
        "carrito_resumen": {
            "total_items": total_items,
            "subtotal": format_price(subtotal),
            "envio_gratis": subtotal >= SHIPPING_THRESHOLD
        }
    }

def ver_carrito() -> dict:
    """
    Muestra el carrito detallado con subtotales, descuentos e impuestos.
    
    Returns:
        dict: Contenido completo del carrito con cálculos.
    """
    logger.info("👀 Mostrando carrito")
    
    if not carrito.items:
        return {
            "status": "empty",
            "message": "🛒 El carrito está vacío.",
            "sugerencia": "Puedes buscar productos disponibles o pedir recomendaciones."
        }
    
    # Build cart summary
    items_detail = []
    for item in carrito.items:
        items_detail.append({
            "nombre": item.nombre,
            "cantidad": item.cantidad,
            "precio_unitario": format_price(item.precio_unitario),
            "subtotal": format_price(item.subtotal)
        })
    
    subtotal = carrito.get_subtotal()
    discount = carrito.get_discount_amount()
    tax = carrito.get_tax()
    shipping = carrito.get_shipping()
    total = carrito.get_total()
    
    resumen = {
        "status": "success",
        "items": items_detail,
        "total_productos": len(carrito.items),
        "total_unidades": sum(item.cantidad for item in carrito.items),
        "calculos": {
            "subtotal": format_price(subtotal),
            "descuento": format_price(discount) if discount > 0 else None,
            "codigo_descuento": carrito.discount_code,
            "impuestos": format_price(tax),
            "envio": format_price(shipping),
            "envio_gratis": shipping == 0,
            "total": format_price(total)
        }
    }
    
    # Add savings message if applicable
    if discount > 0:
        resumen["mensaje_ahorro"] = f"¡Estás ahorrando {format_price(discount)}!"
    if shipping == 0 and subtotal >= SHIPPING_THRESHOLD:
        resumen["mensaje_envio"] = "¡Envío gratis incluido!"
    
    return resumen

def aplicar_descuento(codigo: str) -> dict:
    """
    Aplica un código de descuento al carrito.
    
    Args:
        codigo: Código de descuento a aplicar.
        
    Returns:
        dict: Confirmación con el nuevo total.
    """
    logger.info(f"🎟️ Aplicando código de descuento: {codigo}")
    
    if not carrito.items:
        return {
            "status": "error",
            "message": "❌ El carrito está vacío. Agrega productos antes de aplicar descuentos."
        }
    
    codigo_upper = codigo.strip().upper()
    
    if codigo_upper not in DISCOUNT_CODES:
        return {
            "status": "error",
            "message": f"❌ Código '{codigo}' no válido.",
            "codigos_disponibles": list(DISCOUNT_CODES.keys())
        }
    
    carrito.discount_code = codigo_upper
    descuento_pct = DISCOUNT_CODES[codigo_upper]
    descuento_amt = carrito.get_discount_amount()
    
    return {
        "status": "success",
        "message": f"✅ Código '{codigo_upper}' aplicado: {int(descuento_pct * 100)}% de descuento",
        "descuento": {
            "porcentaje": f"{int(descuento_pct * 100)}%",
            "monto": format_price(descuento_amt),
            "subtotal_original": format_price(carrito.get_subtotal()),
            "total_con_descuento": format_price(carrito.get_total())
        }
    }

def remover_del_carrito(producto: str, cantidad: Optional[int] = None) -> dict:
    """
    Remueve productos del carrito (parcial o completamente).
    
    Args:
        producto: Nombre del producto a remover.
        cantidad: Cantidad a remover (None = remover todo).
        
    Returns:
        dict: Confirmación de la operación.
    """
    logger.info(f"🗑️ Removiendo del carrito: '{producto}' (cantidad: {cantidad})")
    
    result = find_product_fuzzy(producto)
    if not result:
        return {
            "status": "error",
            "message": f"❌ Producto '{producto}' no encontrado en el carrito."
        }
    
    key, product_info = result
    item = get_cart_item_by_product(product_info.id)
    
    if not item:
        return {
            "status": "error",
            "message": f"❌ '{product_info.nombre}' no está en el carrito."
        }
    
    if cantidad is None or cantidad >= item.cantidad:
        # Remove completely
        carrito.items.remove(item)
        return {
            "status": "success",
            "message": f"✅ Removido completamente '{product_info.nombre}' del carrito.",
            "producto_removido": product_info.nombre,
            "cantidad_removida": item.cantidad
        }
    elif cantidad > 0:
        # Remove partially
        item.cantidad -= cantidad
        item.subtotal = item.precio_unitario * item.cantidad
        return {
            "status": "success",
            "message": f"✅ Removidas {cantidad} unidades de '{product_info.nombre}'.",
            "cantidad_removida": cantidad,
            "cantidad_restante": item.cantidad
        }
    else:
        return {
            "status": "error",
            "message": "❌ La cantidad debe ser mayor que cero."
        }

def vaciar_carrito() -> dict:
    """
    Vacía completamente el carrito y resetea descuentos.
    
    Returns:
        dict: Confirmación de la operación.
    """
    logger.info("🧹 Vaciando carrito")
    
    items_count = len(carrito.items)
    units_count = sum(item.cantidad for item in carrito.items)
    
    carrito.items.clear()
    carrito.discount_code = None
    
    return {
        "status": "success",
        "message": "🧹 Carrito vaciado correctamente.",
        "productos_removidos": items_count,
        "unidades_removidas": units_count
    }

def calcular_total() -> dict:
    """
    Calcula el total detallado del carrito incluyendo todos los cargos.
    
    Returns:
        dict: Desglose completo de costos.
    """
    logger.info("💰 Calculando total del carrito")
    
    if not carrito.items:
        return {
            "status": "empty",
            "message": "El carrito está vacío.",
            "total": format_price(0)
        }
    
    subtotal = carrito.get_subtotal()
    discount = carrito.get_discount_amount()
    tax = carrito.get_tax()
    shipping = carrito.get_shipping()
    total = carrito.get_total()
    
    # Build detailed breakdown
    desglose = {
        "status": "success",
        "resumen_productos": [],
        "subtotal": format_price(subtotal),
        "descuento": {
            "codigo": carrito.discount_code,
            "monto": format_price(discount)
        } if discount > 0 else None,
        "impuestos": {
            "tasa": f"{int(TAX_RATE * 100)}%",
            "monto": format_price(tax)
        },
        "envio": {
            "costo": format_price(shipping),
            "gratis": shipping == 0,
            "umbral_gratis": format_price(SHIPPING_THRESHOLD)
        },
        "total": format_price(total),
        "mensaje": f"💳 Total a pagar: {format_price(total)}"
    }
    
    # Add product details
    for item in carrito.items:
        desglose["resumen_productos"].append({
            "producto": item.nombre,
            "cantidad": item.cantidad,
            "precio_unitario": format_price(item.precio_unitario),
            "subtotal": format_price(item.subtotal)
        })
    
    # Add savings information
    ahorros = []
    if discount > 0:
        ahorros.append(f"Descuento: {format_price(discount)}")
    if shipping == 0 and subtotal >= SHIPPING_THRESHOLD:
        ahorros.append(f"Envío gratis: {format_price(SHIPPING_COST)}")
    
    if ahorros:
        desglose["ahorros_totales"] = {
            "items": ahorros,
            "total": format_price(discount + (SHIPPING_COST if shipping == 0 else 0))
        }
    
    return desglose

def recomendar_productos(categoria: Optional[str] = None) -> dict:
    """
    Recomienda productos basados en categoría o popularidad.
    
    Args:
        categoria: Categoría específica para filtrar (opcional).
        
    Returns:
        dict: Lista de productos recomendados.
    """
    logger.info(f"🎯 Generando recomendaciones (categoría: {categoria})")
    
    productos = list(PRODUCTOS_DB.values())
    
    # Filter by category if specified
    if categoria:
        productos = [p for p in productos if p.categoria.lower() == categoria.lower()]
        if not productos:
            return {
                "status": "error",
                "message": f"No hay productos en la categoría '{categoria}'.",
                "categorias_disponibles": list(set(p.categoria for p in PRODUCTOS_DB.values()))
            }
    
    # Sort by rating and reviews
    productos.sort(key=lambda p: (p.rating, p.reviews), reverse=True)
    
    recomendaciones = []
    for p in productos[:3]:  # Top 3
        recomendaciones.append({
            "nombre": p.nombre,
            "precio": format_price(p.precio),
            "rating": f"⭐ {p.rating}/5.0",
            "categoria": p.categoria,
            "descripcion": p.descripcion,
            "disponible": p.stock > 0
        })
    
    return {
        "status": "success",
        "categoria": categoria or "Todas",
        "recomendaciones": recomendaciones,
        "mensaje": f"🌟 Top {len(recomendaciones)} productos recomendados"
    }

def mostrar_historial_busquedas() -> dict:
    """
    Muestra el historial de búsquedas recientes del usuario.
    
    Returns:
        dict: Historial de búsquedas.
    """
    if not historial_busquedas:
        return {
            "status": "empty",
            "message": "No hay búsquedas recientes."
        }
    
    return {
        "status": "success",
        "historial": historial_busquedas[-5:],  # Last 5 searches
        "total_busquedas": len(historial_busquedas)
    }

# -------------------------
# Enhanced Agent Configuration
# -------------------------

root_agent = Agent(
    name="ecommerce_assistant_pro",
    model="gemini-2.5-flash",
    description="Asistente de e-commerce avanzado con búsqueda inteligente, gestión de carrito y recomendaciones personalizadas.",
    instruction=(
        "Eres un asistente de compras profesional y amigable. Tu objetivo es ayudar a los usuarios a:\n"
        "1. Encontrar productos usando búsqueda flexible (no necesitan escribir el nombre exacto)\n"
        "2. Gestionar su carrito de compras eficientemente\n"
        "3. Aplicar descuentos y calcular totales con impuestos y envío\n"
        "4. Recibir recomendaciones personalizadas\n\n"
        "Características especiales:\n"
        "- Búsqueda inteligente: encuentra productos aunque el nombre no sea exacto\n"
        "- Cálculo automático de impuestos (8%) y envío (gratis sobre $100)\n"
        "- Códigos de descuento: WELCOME10 (10%), SAVE20 (20%), VIP30 (30%)\n"
        "- Recomendaciones basadas en popularidad y categoría\n\n"
        "Sé proactivo:\n"
        "- Si no encuentras un producto, sugiere alternativas similares\n"
        "- Menciona cuando el usuario está cerca del envío gratis\n"
        "- Recuerda informar sobre descuentos disponibles\n"
        "- Destaca las características y ratings de los productos"
    ),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=800,
        top_p=0.9
    ),
    tools=[
        buscar_producto_por_nombre,
        agregar_al_carrito,
        ver_carrito,
        aplicar_descuento,
        remover_del_carrito,
        vaciar_carrito,
        calcular_total,
        recomendar_productos,
        mostrar_historial_busquedas
    ],
)