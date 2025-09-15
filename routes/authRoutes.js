const express = require('express');
const router = express.Router();
const { AppDataSource } = require('../data-source');

//------------------Login...................

router.get('/', (req, res) => {
    res.render('login', { error: null });
});

router.post('/login', async (req, res) => {
    const { identifier } = req.body;
    const repo = AppDataSource.getRepository("Registrant");
    const isEmail = identifier.includes('@');  // ✅ Check if it's email

    try {
        const users = await repo.find({
            where: isEmail
                ? { Email: identifier }
                : { Mobile: identifier },
            select: [
                "Id",
                "Name",
                "Designation",
                "Organization",
                ...(isEmail ? ["Email"] : ["Mobile"]),  // ✅ Pick one
                "City",
                "Mode",
                "AttendanceDay1",
                "AttendanceDay2"
            ]
        });

        if (users.length === 0) {
            return res.render('login', { error: "invalid credential" });
        }

        // ✅ Only allow if attended at least one day
        const response = users.filter(
            data => data.AttendanceDay1 || data.AttendanceDay2
        );

        if (response.length > 0) {
            res.render('profile', { users: response });
        } else {
            res.render('login', { error: 'You did not attend the conference' });
        }
    } catch (err) {
        console.error(err);
        res.send('Database error');
    }
});


module.exports = router;