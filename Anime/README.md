## Yandere (Maybe 18+ arts)

| Name                                                         | Description                                           | Download                                                     |
| ------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------ |
| [yandere](https://gitlab.com/CakesTwix/friendly-userbot-modules/-/blob/master/Anime/yandere.py) | Module for obtaining art from the ImageBoard yande.re | .dlmod https://gitlab.com/CakesTwix/friendly-userbot-modules/-/raw/master/Anime/yandere.py |

## Commands

| **Command**                   | Description          |                                                              |
| ----------------------------- | -------------------- | ------------------------------------------------------------ |
| .ylast                        | The last posted art  |                                                              |
| .yrandom                      | Random posted art    |                                                              |
| .yvote [reply [-1, 1, 2, 3] ] | Voting for art.      |                                                              |
| **Config**                    |                      | **Set**                                                      |
| yandere_login                 | Login from yande.re  | .eval next(filter(lambda x: "Yandere" == x.strings["name"], self.allmodules.modules)).config["yandere_login"] = "Your nickname" |
| yandere_password_hash         | SHA1 hashed password | .eval next(filter(lambda x: "Yandere" == x.strings["name"], self.allmodules.modules)).config["yandere_password_hash"] = "Your password" |

## Yandere (Maybe 18+ arts) [ONLY GEEKTG]

| Name                                                         | Description                                           | Download                                                     |
| ------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------ |
| [yandere](https://gitlab.com/CakesTwix/friendly-userbot-modules/-/blob/master/Anime/yandere.py) | Module for obtaining art from the ImageBoard yande.re | .dlmod https://gitlab.com/CakesTwix/friendly-userbot-modules/-/raw/master/Anime/yandere_geek.py |

## Commands

| **Command**                            | Description                                                 |                                                              |
| -------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ |
| .ylast                                 | The last posted art                                         |                                                              |
| .yrandom                               | Random posted art                                           |                                                              |
| .yvote [reply or reply [-1, 1, 2, 3] ] | Voting for art. Provides an Inline keyboard for convenience |                                                              |
| **Config**                             |                                                             | **Set**                                                      |
| yandere_login                          | Login from yande.re                                         | .eval next(filter(lambda x: "Yandere" == x.strings["name"], self.allmodules.modules)).config["yandere_login"] = "Your nickname" |
| yandere_password_hash                  | SHA1 hashed password                                        | .eval next(filter(lambda x: "Yandere" == x.strings["name"], self.allmodules.modules)).config["yandere_password_hash"] = "Your password" |

## NHentai 18+

| Name                                                         | Description        | Download                                                     |
| ------------------------------------------------------------ | ------------------ | ------------------------------------------------------------ |
| [nhentai](https://gitlab.com/CakesTwix/friendly-userbot-modules/-/blob/master/Anime/nhentai.py) | Hentai module 18+" | .dlmod https://gitlab.com/CakesTwix/friendly-userbot-modules/-/raw/master/Anime/nhentai.py |

## Commands

| **Command**      | Description                |
| ---------------- | -------------------------- |
| .nhid id         | Search hentai manga by id  |
| .nhrandom        | Random hentai manga        |
| .nhtag [tag tag] | Search hentai manga by tag |

## AniLibria [ONLY GEEKTG]

| Name                                                         | Description                                                  | Download                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| [anilibria](https://gitlab.com/CakesTwix/friendly-userbot-modules/-/blob/master/Anime/anilibria.py) | A non-profit project for the dubbing and adaptation of foreign TV series, cartoons and anime | .dlmod https://gitlab.com/CakesTwix/friendly-userbot-modules/-/raw/master/Anime/anilibria.py |

## Commands

| **Command**                       | Description                                     |                                                              |
| --------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| .aramdom                          | Возвращает случайный тайтл из базы              |                                                              |
| .aschedule                        | Получить список последних обновлений тайтлов    |                                                              |
| @geektg_######_bot asearch [text] | Возвращает список найденных по названию тайтлов |                                                              |
| **Config**                        |                                                 | **Set**                                                      |
| CONFIG_MAIL                       | Your mail from anilibria.tv                     | .eval next(filter(lambda x: "AniLibria" == x.strings["name"], self.allmodules.modules)).config["CONFIG_MAIL"] = "Your mail" |
| CONFIG_PASS                       | Your password from anilibria.tv                 | .eval next(filter(lambda x: "AniLibria" == x.strings["name"], self.allmodules.modules)).config["CONFIG_PASS"] = "Your password" |
