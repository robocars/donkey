const express = require('express');
const archiver = require('archiver');
const path = require('path');
const fs = require('fs');
const config = require('config');
const {promisify} = require('util');

const readdir = promisify(fs.readdir);
const fsstat = promisify(fs.stat);

const router = express.Router();

router.get('/tubes', async (req, res) => {
    const root = config.get('tubes.root');
    res.json((await readdir(root)).map((dir) => ({
        name: dir,
        url: `/tubes/${dir}`    
    })));
});

router.get('/tubes/:tubId', (req, res) => {
    const root = config.get('tubes.root');
    const archive = archiver('zip');
    archive.pipe(res);
    archive.directory(path.join(root, req.params.tubId));
    archive.finalize();
});

module.exports = router;