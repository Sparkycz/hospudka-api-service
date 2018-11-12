API Service Hospudka (a pub)
=====
This service was built just for purposes of the presentation ("Do not mock the whole world") at Pyvo mini-conference.

Requirements
-----

* Python 3.6
* Docker and Docker Compose

First run
-----

1. Start the service by

```
$ docker-compose build && docker-compose up
```

2. Create database and insert some data to MySQL DB

```sql
CREATE DATABASE `hospudka`;

CREATE TABLE `Beers` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(255) COLLATE utf8_bin NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin
AUTO_INCREMENT=1 ;

INSERT INTO `Beers` (`name`) VALUES ("Kozel");
```

3. Try to call the entry point bellow

Entry point
-----
Contains only one entry point

```
$ curl -XGET http://localhost:8080/beers/<id:int>
```

Run tests
-----

```
$ docker-compose -f docker-compose-tests.yaml up --abort-on-container-exit
```

