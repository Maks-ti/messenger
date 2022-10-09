
/* --- --- --- user and more --- --- --- */

/* таблица описывающая User`а */
CREATE TABLE users (
id SERIAL PRIMARY KEY,
login VARCHAR(50) UNIQUE,
password_hash VARCHAR(128),
name VARCHAR(50) NOT NULL
);

/* таблица содержащая информацию пользователя
один к одному с таблицей user
создана для оптимизации 
(данные из user используются чаще чем из profile_info) */
CREATE TABLE profile_info (
user_id INTEGER PRIMARY KEY REFERENCES users(id),
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
PRIMARY KEY (follower_id, followed_id)
);

/* --- --- --- чаты и сообжения --- --- --- */

/* таблица описывающая чат (беседу) 
// надо будет накинуть триггер на таблицу user in chat
// что бы при добавлении (удалении) юзера в чат
// счётчик user`ов автоматически обновлялся
*/
CREATE TABLE chat (
id SERIAL PRIMARY KEY,
name VARCHAR(50) NOT NULL,
counter INTEGER NOT NULL,
image BYTEA
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
id SERIAL PRIMARY KEY,
chat_id INTEGER NOT NULL REFERENCES chat(id) ON DELETE CASCADE,
user_id INTEGER NOT NULL REFERENCES users(id),
parent_id INTEGER REFERENCES message(id) ON DELETE CASCADE,
mes_text TEXT NOT NULL,
sends_time TIMESTAMP NOT NULL
);

/*--- --- --- посты и коменты --- --- --- */

/* таблица описывающая пост */
CREATE TABLE post (
id SERIAL PRIMARY KEY,
user_id INTEGER NOT NULL REFERENCES users(id),
title VARCHAR (200) NOT NULL,
publication_date TIMESTAMP NOT NULL,
last_edit_date TIMESTAMP,
post_text TEXT NOT NULL,
image BYTEA
);

/* таблица описывающая комментарий к посту */
CREATE TABLE comment (
id SERIAL PRIMARY KEY,
post_id INTEGER NOT NULL REFERENCES post(id) ON DELETE CASCADE,
commentator_id INTEGER NOT NULL REFERENCES users(id),
parent_id INTEGER REFERENCES comment(id) ON DELETE CASCADE,
comment_text TEXT NOT NULL,
sends_time TIMESTAMP NOT NULL
);


/*

DROP TABLE comment;
DROP TABLE post;
DROP TABLE message;
DROP TABLE user_in_chat;
DROP TABLE chat;
DROP TABLE follows;
DROP TABLE profile_info;
FROP TABLE users;

*/



