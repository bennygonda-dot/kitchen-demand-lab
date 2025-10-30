"""UK Cooking Appliance Datasets - Core Models Package

Production-grade data pipeline for long-run UK cooking appliance market analysis.
Segments by income deciles and home-price deciles (New Build vs R&R).
"""

__version__ = "1.0.0"

from . import ingest
from . import clean
from . import hhfce
from . import deciles_income
from . import ppd_deciles
from . import newbuild_pool
from . import rr_anchor
from . import range_share
from . import price_bands
from . import panels
from . import charts

__all__ = [
    "ingest",
    "clean",
    "hhfce",
    "deciles_income",
    "ppd_deciles",
    "newbuild_pool",
    "rr_anchor",
    "range_share",
    "price_bands",
    "panels",
    "charts",
]
