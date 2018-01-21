const request = require('superagent');

export const getModels = async (baseUrl) => {
    const resp = await request.get(`${baseUrl}/models`);
    return (resp || {}).body || [];
}

