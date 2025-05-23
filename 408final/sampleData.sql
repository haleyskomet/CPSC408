INSERT INTO User(name)
VALUES ('John');

INSERT INTO User(name)
VALUES ('Brad');

INSERT INTO User(name)
VALUES ('Peter');

INSERT INTO League(name, sport_id)
VALUES ('Premier League', 2);

INSERT INTO League(name, sport_id)
VALUES ('NBA', 1);

INSERT INTO League(name, sport_id)
VALUES ('NFL', 3);

INSERT INTO Sport(name)
VALUES ('Basketball');

INSERT INTO Sport(name)
VALUES ('Soccer');

INSERT INTO Sport(name)
VALUES ('Football');

INSERT INTO Game(winner_team, loser_team, score, date, league_id)
VALUES('Newcastle', 'Manchester United', '4-1', '2025-04-13 8:30:00', 1);

INSERT INTO Game(winner_team, loser_team, score, date, league_id)
VALUES('Golden State Warriors', 'Houston Rockets', '95-85', '2025-04-20 18:30:00', 2);

INSERT INTO Game(winner_team, loser_team, score, date, league_id)
VALUES('Philadelphia Eagles', 'Kansas City Chiefs', '40-22', '2025-02-09 15:00:00', 3);

INSERT INTO Post(rating, comment, game_id, user_id)
VALUES (3, 'wanted ManU to win', 1, 1);

INSERT INTO Post(rating, comment, game_id, user_id)
VALUES (4, 'It was a good game', 2, 2);

INSERT INTO Post(rating, comment, game_id, user_id)
VALUES (5, 'Love the Eagles!', 3, 3);

ALTER TABLE Sport
DROP FOREIGN KEY sport_ibfk_1;