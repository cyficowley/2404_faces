import mysql.connector
from SuperSecretPasswords import passwd
import time
"""
CREATE TABLE IF NOT EXISTS `enterances` (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
    `name` varchar(24) NOT NULL COMMENT 'the persons name',
    `time` DATE COMMENT 'time seen',
    `distance` DOUBLE COMMENT 'eucleadian distance to selected face',
    `difference` DOUBLE COMMENT 'face match percentage vs closest',
    PRIMARY KEY (`id`)
);
"""

class database():
    def __init__(self):
        self.db = mysql.connector.connect(
            host ="faceslogdata.c3yjyqef1jbu.us-west-1.rds.amazonaws.com",
            user="cyficowley",
            database="FacesTimeLog",
            passwd=passwd
        )

        self.curr = self.db.cursor()


    def add_row(self, name, surity, difference):
        add_row = "INSERT INTO `enterances` (name, time, distance, difference) VALUES ('{}', '{}', '{}', '{}')"
        command_str = add_row.format(name, time.strftime('%Y-%m-%d %H:%M:%S'), surity, difference)
        self.curr.execute(command_str)
        self.db.commit()

    def shutdown(self):
        self.curr.close()
        self.db.close()



