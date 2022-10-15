
/* --- --- --- user and more --- --- --- */

/* таблица описывающая User`а */
CREATE TABLE users (
id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
login VARCHAR(50) UNIQUE,
password_hash VARCHAR(128),
name VARCHAR(50) NOT NULL
);

/* таблица содержащая информацию пользователя
один к одному с таблицей user
создана для оптимизации 
(данные из user используются чаще чем из profile_info) */
CREATE TABLE profile_info (
id INTEGER PRIMARY KEY REFERENCES users(id),
profile_img BYTEA,
biography TEXT,
about TEXT
);

/* таблица описывающая подписки между User`ами (связь многие ко многим между user и user)
подразумевается, что id в таблице user не меняется поэтому 
ограничения прописываются только в случае удаления */
CREATE TABLE follows (
follower_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
followed_id INTEGER REFERENCES users(id),
PRIMARY KEY (follower_id, followed_id),
CHECK(follower_id <> followed_id)
);

/* --- --- --- чаты и сообжения --- --- --- */

/* таблица описывающая чат (беседу) 
// надо будет накинуть триггер на таблицу user in chat
// что бы при добавлении (удалении) юзера в чат
// счётчик user`ов автоматически обновлялся
*/
CREATE TABLE chat (
id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
name VARCHAR(50) NOT NULL,
counter INTEGER NOT NULL DEFAULT 0,
image BYTEA DEFAULT NULL
);

/* таблица реализующая связь многие ко многим для chat и user */
CREATE TABLE user_in_chat(
user_id INTEGER,
chat_id INTEGER,
PRIMARY KEY (user_id, chat_id)
);

/* таблица описывающая сообщение (в рамках чата) 
аналогично как и с user`ом предполагаем что у чата id не меняется никогда
значит и проверку на обновление не ставим
--
что касается parent_id - это ссылка на родительское сообщение
то еть на сообщение, на которое отвечает данное сообщение (данное поле не являетс обязательным к заполнению)
*/
CREATE TABLE message (
id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE,
user_id INTEGER NOT NULL REFERENCES users(id),
parent_id INTEGER REFERENCES message(id) ON DELETE CASCADE,
mes_text TEXT NOT NULL,
sends_time TIMESTAMP NOT NULL
);

/*--- --- --- посты и коменты --- --- --- */

/* таблица описывающая пост */
CREATE TABLE post (
id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
user_id INTEGER NOT NULL REFERENCES users(id),
title VARCHAR (200) NOT NULL,
publication_date TIMESTAMP NOT NULL,
last_edit_date TIMESTAMP,
post_text TEXT NOT NULL,
image BYTEA
);

/* таблица описывающая комментарий к посту */
CREATE TABLE comment (
id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
post_id INTEGER NOT NULL REFERENCES post(id) ON DELETE CASCADE,
commentator_id INTEGER NOT NULL REFERENCES users(id),
parent_id INTEGER REFERENCES comment(id) ON DELETE CASCADE,
comment_text TEXT NOT NULL,
sends_time TIMESTAMP NOT NULL
);

/* --- --- --- функции и триггеры --- --- --- */

CREATE FUNCTION counter_updater() RETURNS trigger AS $counter_updater$
	BEGIN
		/*если операция insert*/
		IF TG_OP = 'INSERT' THEN
			/*увеличиваем счётчик пользователей*/
			UPDATE chat
				SET counter = counter + 1
				WHERE id = NEW.chat_id
				;
		END IF;
		
		/*если операция delete*/
		IF TG_OP = 'DELETE' THEN
			/*уменьшаем счётчик пользователей*/
			UPDATE chat
				SET counter = counter - 1
				WHERE id = NEW.chat_id
				;			
		END IF;	
		RETURN NEW;	
	END;
$counter_updater$ LANGUAGE plpgsql;


CREATE TRIGGER counter_updater AFTER INSERT OR DELETE ON user_in_chat
	FOR EACH ROW EXECUTE PROCEDURE counter_updater();



/*

DROP TRIGGER counter_updater ON user_in_chat;
DROP FUNCTION counter_updater;
DROP TABLE comment;
DROP TABLE post;
DROP TABLE message;
DROP TABLE user_in_chat;
DROP TABLE chat;
DROP TABLE follows;
DROP TABLE profile_info;
DROP TABLE users;

*/

/*
INSERT INTO users(login, password_hash, name) VALUES('log1', 'hash1', 'name1');
INSERT INTO users(login, password_hash, name) VALUES('log2', 'hash2', 'name2');
INSERT INTO chat(name) VALUES ('chat name 1');
INSERT INTO user_in_chat(user_id, chat_id) VALUES(1, 1);
INSERT INTO user_in_chat(user_id, chat_id) VALUES(2, 1);
*/



