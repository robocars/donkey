import config from '../config';
const request = require('superagent');

export const getTubes = async () => {
    const resp = await request.get(`${config.apiBaseUrl}/tubes`);
    return (resp || {}).body || [];
}

