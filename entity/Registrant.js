const { EntitySchema } = require("typeorm");

module.exports = new EntitySchema({
  name: "Registrant",          // Entity name
  tableName: "registrants",    // Table name in DB
  columns: {
    Id: { type: Number, primary: true, generated: true },

    Name: { type: String, length: 255, nullable: false },
    Designation: { type: String, length: 255, nullable: false },
    Organization: { type: String, length: 255, nullable: false },
    Email: { type: String, length: 255, nullable: false, unique: false},
    Mobile: { type: String, length: 255, nullable: false },
    City: { type: String, length: 255, nullable: false },
    Mode: { type: String, length: 255, nullable: false },

    AttendanceDay1: { type: Boolean, default: false },
    AttendanceDay2: { type: Boolean, default: false },

    regtime: { type: Date, createDate: true } // auto timestamp
  }
});

