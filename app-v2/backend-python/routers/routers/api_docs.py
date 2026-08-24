from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ..spec.openapi import OPENAPI_TAG_NAME

from core.singleton.logger import loggerHTTP as logger

router = APIRouter(
  prefix="/api-docs", 
  tags=[OPENAPI_TAG_NAME.API_DOCS], 
)

@router.get("/scalar", 
            operation_id="apiDocsGetScalarUI",
            summary="Scalar UI",
            description="Webpage (HTML) for API Reference using Scalar UI",
            )
async def apiDocsGetScalarUI() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html>
<head>
    <title>API Reference</title>
    <meta charset="utf-8" />
</head>
<body>
<div id="app"></div>

<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>

<script>
Scalar.createApiReference('#app', {
    // The URL to the OpenAPI JSON file used as input
    url: '/openapi.json',
    
    // You can specify the path to a favicon to be used for the documentation.
    // favicon: '',
    
    // The theme to use
    // Can be one of: 
    // - alternate
    // - default
    // - moon
    // - purple
    // - solarized
    // - bluePlanet
    // - saturn
    // - kepler
    // - mars
    // - deepSpace
    // - laserwave
    // - none
    theme: 'default',
    
    // The layout of UI
    // Can be one of:
    // - classic
    // - modern
    layout: 'modern',
    
    // Whether to show the sidebar initially
    showSidebar: true,
    
    // Whether to show the sidebar search bar.
    hideSearch: false,
    
    // Whether to show the "Test Request" button. 
    // When true, the authentication panel is also hidden, since it is only relevant when test requests are available.
    hideTestRequestButton: false,
    
    // Whether to enable dark mode initially
    darkMode: true,
    
    // Whether to open the first tag if the URL doesn't contain a specific target.
    defaultOpenFirstTag: true,
    
    // Whether to always start with all tags open, regardless of the URL
    defaultOpenAllTags: false,
    
    // By default the models are all closed in the model section at the bottom, this flag will open them all by default.
    expandAllModelSections: true,
    
    // By default response sections are closed in the operations. This flag will open them by default
    expandAllResponses: false,
    
    // When true, nested child properties are expanded by default. 
    // The "Show/Hide Child Attributes" toggle stays available so users can collapse sections manually.
    // Warning: this can cause performance issues on big documents.
    expandAllSchemaProperties: false,
    
    // Every operation can have a operationId, a unique string used to identify the operation, but it's optional.
    // By default we don't render it in the UI. If it's helpful to show it to your users, enable it
    showOperationId: true,
    
    // Whether the sidebar display text and search should use the operation summary or the operation path.
    //
    // Type: 'summary' | 'path'
    // Default: 'summary'
    operationTitleSource: 'summary', 
    
    // Whether models (components.schemas or definitions) should be shown in the sidebar, search and content.
    hideModels: false,
    
    // Label for the components.schemas section in the sidebar, main content, and search. 
    // Use Schemas for OpenAPI terminology; 
    // Models is the default for backward compatibility. 
    // Any custom string is supported.
    // 
    // Type: 'Models' | 'Schemas' | string
    // Default: 'Models'
    modelsSectionLabel: 'Models',
    
    // Whether to order required properties first in schema objects. 
    // When enabled, required properties will be displayed before optional properties in model definitions.
    orderRequiredPropertiesFirst: false,
    
    // Control how schema properties are ordered in model definitions. 
    // Can be set to:
    // - 'alpha': Sort properties alphabetically by name
    // - 'preserve': Preserve the order from the OpenAPI Document
    // Default: 'alpha'
    orderSchemaPropertiesBy: 'preserve',
    
});
</script>
</body>
</html>
"""
    )