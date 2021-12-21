## Yandere (Maybe 18+ arts)

| Name                                                         | Description                                           | Download                                                     |
| ------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------ |
| [yandere](https://gitlab.com/CakesTwix/friendly-userbot-modules/-/blob/master/Anime/yandere.py) | Module for obtaining art from the ImageBoard yande.re | .dlmod https://gitlab.com/CakesTwix/friendly-userbot-modules/-/raw/master/Anime/yandere.py |

## Commands

| **Command**           | Description          |                                                              |
| --------------------- | -------------------- | ------------------------------------------------------------ |
| .ylast                | The last posted art  |                                                              |
| .yrandom              | Random posted art    |                                                              |
| **Config**            |                      | **Set**                                                      |
| yandere_login         | Login from yande.re  | .eval next(filter(lambda x: "Yandere" == x.strings["name"], self.allmodules.modules)).config["yandere_login"] = "Your nickname" |
| yandere_password_hash | SHA1 hashed password | .eval next(filter(lambda x: "Yandere" == x.strings["name"], self.allmodules.modules)).config["yandere_password_hash"] = "Your password" |

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
