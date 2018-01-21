const request = require('superagent');

export const getTubes = async (baseUrl) => {
    const resp = await request.get(`${baseUrl}/tubes`);
    return (resp || {}).body || [];
}

