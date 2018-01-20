const express = require('express');
const path = require('path');
const fs = require('fs');
const config = require('config');
const {promisify} = require('util');
const multer = require('multer');

const model_upload = multer({ dest: config.get('models.root') })

const readdir = promisify(fs.readdir);

const router = express.Router();

router.get('/models', async (req, res) => {
    const root = config.get('models.root');
    res.json((await readdir(root)).map((dir) => ({
        name: dir,
        url: `/models/${dir}`    
    })));
});

router.post('/models', model_upload.single('model'), async (req, res) => {
    res.json({
        status: 'OK'
    })
});

module.exports = router;