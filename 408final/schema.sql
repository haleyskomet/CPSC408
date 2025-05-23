CREATE DATABASE sportsLetterboxd;
USE sportsLetterboxd;

CREATE TABLE User(
    user_id INT AUTO_INCREMENT,
    name VARCHAR (100),
    password VARCHAR(100),
    PRIMARY KEY (user_id)
);

CREATE TABLE Sport(
    sport_id INT AUTO_INCREMENT,
    name VARCHAR (50),
    PRIMARY KEY (sport_id)
);

CREATE TABLE League(
    league_id INT AUTO_INCREMENT,
    name VARCHAR (100),
    sport_id INT,
    PRIMARY KEY (league_id),
    FOREIGN KEY (sport_id) REFERENCES Sport(sport_id)
);

CREATE TABLE Game(
    game_id INT AUTO_INCREMENT,
    winner_team VARCHAR (100),
    loser_team VARCHAR (100),
    score VARCHAR (100),
    date DATETIME,
    league_id INT,
    PRIMARY KEY (game_id),
    FOREIGN KEY (league_id) REFERENCES League(league_id)
);

CREATE TABLE Post(
    post_id INT AUTO_INCREMENT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment VARCHAR(500),
    game_id INT,
    user_id INT,
    PRIMARY KEY (post_id),
    FOREIGN KEY (game_id) REFERENCES Game(game_id),
    FOREIGN KEY (user_id) REFERENCES User(user_id)
);


