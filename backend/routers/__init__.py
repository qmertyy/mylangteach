from routers.config_router import router as config_router
from routers.chats_router import router as chats_router
from routers.categories_router import router as categories_router
from routers.documents_router import router as documents_router
from routers.grammar_router import router as grammar_router
from routers.audio_router import router as audio_router

all_routers = [
    config_router,
    chats_router,
    categories_router,
    documents_router,
    grammar_router,
    audio_router,
]
