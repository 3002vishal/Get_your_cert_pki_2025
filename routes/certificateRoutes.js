const express = require('express');
const router = express.Router();
const {AppDataSource} = require('../data-source');
const path = require('path');
const {spawn} = require('child_process');

router.get('/certificate/:id',async (req , res) => 
{
    const {id} = req.params;
    const repo = AppDataSource.getRepository("Registrant");
    try{
        const user = await repo.findOneBy({Id:id});

        if(!user) return res.send('User not found');
        let certFile = null;
    
        //--selecting file based on user attendence---

        if(user.AttendanceDay1 && !user.AttendanceDay2)
            certFile = '1.pdf';
        else if(!user.AttendanceDay1 && user.AttendanceDay2)
            certFile = '2.pdf';
        else if(user.AttendanceDay1 && user.AttendanceDay2)
            certFile = '0.pdf';
        else return res.render("cert_error",{message: "You did not attend the PKI 2025 conference , certificate could not be provided"});

        const certPath = path.join(__dirname, '../certs', certFile);  // creating certificate path

        //--calling the python as subprocess to generate the certificate 

        const python = spawn('python', [
            path.join(__dirname, '../pdfeditor/pdfeditor.py'),
            certPath,
            user.Name
        ]);

        let chunks = [];  // creates an empty array to  store chunks of binary pdf content returned by python script
        
        //--listens to puthon script everytime python sends some data, pushed into chunks.
        
        python.stdout.on('data', (data) => {
            chunks.push(data);
        });

        //--Listen to python error output and logs any error message

        python.stderr.on('data', (data)=> {
            console.error(`python error: ${data}`);
        });

        python.on('close', (code) => {
            if(code !==0) return res.send("Error generating certificate"); // send error response
            
            const pdfBuffer = Buffer.concat(chunks);
            res.setHeader('Content-Disposition', `attachment; filename=certificate_${user.Name}.pdf`);  // sets Http header to that browser downloads the file
            res.setHeader('Content-Type', 'application/pdf'); // tells browser it's a pdf
            res.send(pdfBuffer);

        });


    }
    catch(err){
        console.error(err);
        res.render("cert_error",{message:"Unexpected server error while generating certificate"});
    }


});
 
module.exports = router;


