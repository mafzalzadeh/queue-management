/*eslint-disable */
const config = {
    APP_API_URL: 'http://localhost:5000/api/v1/',
    SOCKET_URL: '"http://localhost:5000"',
    REFRESH_TOKEN_SECONDS_LEFT: process.env.VUE_APP_REFRESH_TOKEN_SECONDS_LEFT || '180',
  KEYCLOAK_JSON_URL: '"http://localhost:8080/static/keycloak.json"',

    BASE_URL: process.env.BASE_URL || '',
    IS_INTERNET_EXPLORER: isInternetExplorer()
}

// localhost and OpenShfit can return strings/envs, so we handle both
// eg handles true and "true"
function handleBooleanString(input: string | Boolean): Boolean {
    if (!input) return false;
    if (typeof input === 'boolean') return input;
    if (typeof input === 'string') {
        return input.toLowerCase() === 'true';
    }
    return false;
}


// We check this here, so it's only ever done once in the entire application
function isInternetExplorer(): boolean {
    // MSIE = IE10 and lower
    // Trident = IE11
    return window.navigator.userAgent.match(/(MSIE|Trident)/) !== null;
}

export default { ...config }
