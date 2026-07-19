"""Taxonomías cerradas para una categorización fiable de las prendas."""

# Categoría general de la prenda (define su rol en el outfit).
CATEGORIAS = [
    "superior",       # camiseta, camisa, blusa, jersey, sudadera
    "inferior",       # pantalón, falda, short
    "vestido",        # vestido, mono (una sola pieza)
    "abrigo",         # chaqueta, abrigo, blazer, cazadora
    "calzado",        # zapatos, zapatillas, botas, sandalias
    "accesorio",      # cinturón, bufanda, gorra, bolso, gafas
]

# Tipo concreto de prenda dentro de cada categoría.
TIPOS = [
    # superior
    "camiseta", "camisa", "blusa", "polo", "jersey", "sudadera", "top",
    # inferior
    "pantalon", "vaqueros", "chino", "falda", "short", "leggings",
    # vestido
    "vestido", "mono",
    # abrigo
    "chaqueta", "blazer", "abrigo", "cazadora", "cardigan", "gabardina",
    # calzado
    "zapatillas", "zapatos", "botas", "sandalias", "mocasines", "tacones",
    # accesorio
    "cinturon", "bufanda", "gorra", "sombrero", "bolso", "gafas", "corbata", "reloj",
]

COLORES = [
    "negro", "blanco", "gris", "azul", "azul marino", "celeste",
    "rojo", "rosa", "verde", "amarillo", "naranja", "morado",
    "marron", "beige", "camel", "crema", "dorado", "plateado", "multicolor",
]

PATRONES = ["liso", "rayas", "cuadros", "estampado", "floral", "lunares", "animal print", "logo"]

MATERIALES = ["algodon", "lino", "lana", "vaquero", "cuero", "sintetico", "punto", "seda", "poliester", "desconocido"]

ESTILOS = ["casual", "formal", "deportivo", "elegante", "urbano", "boho", "clasico", "minimalista"]

TEMPORADAS = ["primavera", "verano", "otoño", "invierno", "todo el año"]

# 1 = muy informal, 5 = muy formal.
FORMALIDAD = [1, 2, 3, 4, 5]

OCASIONES = ["trabajo", "casual", "cita", "deporte", "formal", "fiesta", "viaje", "casa"]
