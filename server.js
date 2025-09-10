require("reflect-metadata"); // required by TypeORM
const express = require('express');
const bodyParser = require('body-parser');
const { AppDataSource } = require('./data-source');
const Registrant = require('./entity/Registrant.js');
const fs = require('fs');
const path = require('path');
const { PDFDocument, StandardFonts, rgb } = require('pdf-lib');

const app = express();
const port = 3000;

app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');

// Initialize TypeORM
AppDataSource.initialize()
  .then(() => console.log("✅ Database connected with TypeORM"))
  .catch(err => console.error("DB connection error:", err));

// ---------------- LOGIN ----------------
app.get('/', (req, res) => {
  res.render('login', { error: null });
});

app.post('/login', async (req, res) => {
  const { identifier } = req.body; // Id, Mobile, or Email
  const repo = AppDataSource.getRepository("Registrant");

  try {
    const user = await repo.findOne({
      where: [
        { Id: identifier },
        { Mobile: identifier },
        { Email: identifier }
      ]
    });

    if (user) {
      res.render('profile', { user });
    } else {
      res.render('login', { error: 'Invalid credentials' });
    }
  } catch (err) {
    console.error(err);
    res.send('Database error');
  }
});

// ---------------- CERTIFICATE ----------------
const { spawn } = require('child_process');

app.get('/certificate/:id', async (req, res) => {
  const { id } = req.params;
  const repo = AppDataSource.getRepository("Registrant");

  try {
    const user = await repo.findOneBy({ Id: id });
    if (!user) return res.send('User not found');

    // Select certificate template based on attendance
    let certFile = '0.pdf';
    if (user.AttendanceDay1 && !user.AttendanceDay2) certFile = '1.pdf';
    else if (!user.AttendanceDay1 && user.AttendanceDay2) certFile = '2.pdf';

    const certPath = path.join(__dirname, 'certs', certFile);

    // Call Python script
    const python = spawn('python', [
      path.join(__dirname, 'pdfeditor/pdfeditor.py'),
      certPath,
      user.Name
    ]);

    let chunks = [];

    python.stdout.on('data', (data) => {
      chunks.push(data);
    });

    python.stderr.on('data', (data) => {
      console.error(`Python error: ${data}`);
    });

    python.on('close', (code) => {
      if (code !== 0) {
        return res.send('Error generating certificate');
      }

      const pdfBuffer = Buffer.concat(chunks);
      res.setHeader('Content-Disposition', `attachment; filename=certificate_${user.Name}.pdf`);
      res.setHeader('Content-Type', 'application/pdf');
      res.send(pdfBuffer);
    });

  } catch (err) {
    console.error(err);
    res.send('Error generating certificate');
  }
});



app.listen(port, () => console.log(`Server running at http://localhost:${port}`));
