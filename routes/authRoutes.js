const express = require('express');
const router = express.Router();
const {AppDataSource} = require('../data-source');

//------------------Login...................

router.get('/', (req, res)=>{
    res.render('login', {error: null});
});

router.post('/login', async(req, res) =>{
    const {identifier} = req.body;
    const repo  = AppDataSource.getRepository("Registrant");
    try {
        const users = await repo.find({
            where:[
            {Id: identifier}, 
            {Mobile: identifier}, 
            {Email: identifier}
            ]

        });

        if(users && users.length > 0 )
        {
            res.render('profile', {users});
        }

        else {
            res.render('login', {error: 'invalid credentials'});
        }
    }
        catch(err){
            console.error(err);
            res.send('Database error');
        } 
});
 
module.exports =  router;