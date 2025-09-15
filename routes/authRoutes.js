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
        const users = await repo
            .createQueryBuilder("user")
            .select([
                "user.Id AS Id",
                "user.Name AS Name",
                "user.Designation AS Designation",
                "user.Organization AS Organization",
                isEmail ? "user.Email AS Email" : "user.Mobile AS Mobile",
                "user.City AS City",
                "user.Mode AS Mode",
                "user.AttendanceDay1 AS Day1",
                "user.AttendanceDay2 AS Day2"
            ])
            .where(isEmail ? "user.Email = :identifier" : "user.Mobile = :identifier", { identifier })
            .getRawMany();

        if (users.length === 0) {
            return res.render('login', { error: "Invalid credential" });
        }
        else  {
            res.render('profile', { users });
        } 
    } catch (err) {
        console.error(err);
        res.send('Database error');
    }
});

module.exports = router;
