<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Elouahabi-Naoufal/SQLiteExplorer">
    <img src="resources/sqlite_manager.png" alt="SQLiteExplorer logo" width="80" height="80">
  </a>

  <h3 align="center">SQLiteExplorer</h3>

  <p align="center">
    A PyQt6 desktop client for browsing and editing SQLite files, with a SQL console,
    charting, CSV/JSON transfer and SQLCipher support.
    <br />
    <a href="https://github.com/Elouahabi-Naoufal/SQLiteExplorer"><strong>Explore the source »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Elouahabi-Naoufal/SQLiteExplorer/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/Elouahabi-Naoufal/SQLiteExplorer/issues">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

SQLiteExplorer (formerly `dbgui`) is a cross-platform desktop front end for SQLite database files,
written in Python with PyQt6. It opens a `.sqlite`/`.db` file directly from disk — there is no server,
no daemon and no configuration file.

The window is a split view: a schema tree on the left, a tabbed data workspace on the right. Clicking a
table opens it in its own tab, so several tables can stay open side by side.

What it does:

* **Schema navigation** — table tree loaded from `sqlite_master`, refreshed on demand.
* **Record editing** — inline cell editing plus a record editor dialog that renders a widget per declared
  column type. Deletion works on the current selection, so a multi-row selection deletes in one pass.
* **SQL console** — run `SELECT`, DML and DDL, inspect results in a grid, or ask SQLite for
  `EXPLAIN QUERY PLAN` output.
* **Query manager** — executed statements are appended to a history file (capped at 100 entries) and any
  statement can be starred into a named favourites list.
* **Pagination** — records are fetched with `LIMIT`/`OFFSET`; page size is adjustable from 10 to 1000.
* **Search and filter** — a `LIKE` search across either all `TEXT`/`VARCHAR` columns or one selected column,
  applied server-side rather than in the widget.
* **Import / export** — export the visible page to CSV or JSON, import a CSV/JSON file with an explicit
  column mapping and a preview step, or run a bulk export of several tables into one output directory.
* **Charts** — bar, line, pie, histogram and scatter plots built with matplotlib over the loaded rows,
  with X/Y column pickers.
* **Backup and restore** — file-level copy of the open database to and from a chosen path.
* **Encrypted files** — if `pysqlcipher3` is installed and a password is supplied, the connection is opened
  through SQLCipher instead of the stdlib driver.
* **Theming** — light and dark stylesheets; the system palette lightness is read at startup to pick the default.

Everything is local-first: no telemetry, no network calls, no account. State that outlives a run is written
next to the working directory as plain JSON (`session.json`, `query_history.json`, `query_favorites.json`),
and logs go to `~/sqlite_manager.log`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python.com]][Python-url]
* [![PyQt6][PyQt6.com]][PyQt6-url]
* [![SQLite][SQLite.com]][SQLite-url]
* [![SQLCipher][SQLCipher.com]][SQLCipher-url]
* [![Matplotlib][Matplotlib.com]][Matplotlib-url]
* [![pandas][pandas.com]][pandas-url]
* [![PyInstaller][PyInstaller.com]][PyInstaller-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

To run SQLiteExplorer from source you need a Python interpreter and the dependencies listed in
`requirements.txt`.

### Prerequisites

* Python 3.9 or newer. The code uses PEP 585 builtin generics (`tuple[bool, str]`) in annotations.
* The Qt 6 runtime libraries shipped with the PyQt6 wheels — on Debian/Ubuntu these are pulled in as
  `libegl1` and `libxkbcommon-x11-0`; the AppImage bundles its own.
* Linux, macOS or Windows.

`pysqlcipher3` is optional. Without it, encrypted databases cannot be opened; everything else works.
If its wheel does not exist for your platform you may need a working C toolchain to build it:

```sh
sudo apt install build-essential libsqlcipher-dev   # Debian/Ubuntu, only for pysqlcipher3
```

### Installation

1. Clone the repository

   ```sh
   git clone https://github.com/Elouahabi-Naoufal/SQLiteExplorer.git
   cd SQLiteExplorer
   ```

2. Create a virtual environment and install the dependencies

   ```sh
   python3 -m venv venv
   source venv/bin/activate          # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Launch the application

   ```sh
   python3 main.py
   ```

<details>
<summary>Build a Linux AppImage</summary>

`create_appimage.sh` produces a self-contained binary: it creates a throwaway virtualenv, freezes
`main.py` with PyInstaller, assembles an AppDir with a desktop entry and `AppRun`, then packs it with
`appimagetool`. Output: `SQLite-Manager-1.0.0-x86_64.AppImage`. The script downloads `appimagetool`
itself if the copy in the repo root is missing.

```sh
chmod +x create_appimage.sh
./create_appimage.sh
```

The generated `.desktop` file and the one checked into the repo both run
`/opt/SQLite-Manager-1.0.0-x86_64.AppImage`, so edit the `Exec=` line if you install the AppImage
somewhere else:

```sh
sudo cp SQLite-Manager-1.0.0-x86_64.AppImage /opt/
sudo cp resources/sqlite_manager.png ~/.local/share/icons/hicolor/256x256/apps/sqlite-manager.png
cp sqlite-manager.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### Connect and browse

`File → Connect to Database…` (`Ctrl+O`) opens the connection dialog. Browse for a file, tick
*Use encryption* to supply a SQLCipher password, or pick one of the recently opened databases.
The driver tries plain `sqlite3` first and only falls back to SQLCipher if that fails or a password was
given. Foreign keys are enabled with `PRAGMA foreign_keys = ON` on every connection.

Click a table in the left tree to open it. The tab loads the schema, then the first page of records.

### Edit data

* Click any cell and type — the change is written straight to the database on commit. Updates are keyed on
  the primary key when the table has one; for keyless tables every column is matched.
* `➕` opens the record editor dialog for a new row, `✏️` re-opens it for the selected row with the
  current values loaded.
* `🗑️` deletes every selected row after a confirmation prompt. The view is in extended-selection mode,
  so `Ctrl`/`Shift`-click multi-row selections work.

### Run SQL

`Edit → Execute SQL…` (`Ctrl+E`) opens the console. `F5` executes, and *Explain Query Plan* returns
SQLite's own plan output for the statement under the cursor. Results render in a grid; DML and DDL report
rows affected. Saved statements are managed from `Edit → Query Manager…` (`Ctrl+H`), which has a History
tab and a Favorites tab — favorites take a name and an optional description.

```sql
-- Run this from the SQL console (Ctrl+E, then F5)
SELECT c.name AS customer,
       COUNT(o.id) AS orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY orders DESC;
```

### Move data in and out

* `📤` exports the rows currently loaded in the tab. Choose `.csv` or `.json` in the save dialog.
* `📥` opens Bulk Import: pick a CSV or JSON file, review the preview, map source columns to table
  columns, then insert.
* `File → Bulk Export…` walks every selected table and writes one file per table into a directory you choose.
* `📊` opens the visualizer for the loaded rows. Pick a chart type (bar, line, pie, histogram, scatter),
  an X column and a Y column.

### Backups

`File → Backup Database…` copies the open file to a path you choose; `File → Restore Database…` copies it
back. Both are plain file copies, so back up a database that no transaction is currently writing to.

### Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Connect to database |
| `Ctrl+E` | Open the SQL console |
| `Ctrl+H` | Open the query manager |
| `F5` | Execute the statement in the SQL console; refresh via the View menu |
| `Ctrl+Q` | Quit |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

Shipped and present in this tree:

- [x] Schema tree, tabbed table workspace, inline editing and multi-row delete
- [x] SQL console with `EXPLAIN QUERY PLAN`, history and favourites
- [x] CSV/JSON export, CSV/JSON import with column mapping, multi-table bulk export
- [x] Matplotlib charts, backup/restore, light and dark themes, session restore

Known gaps in the current code:

- [ ] Charting uses the matplotlib `Qt5Agg` backend while the UI is PyQt6; confirm a working binding
      before relying on the visualizer
- [ ] The schema tree lists tables only. `SchemaManager` already has helpers for views, indexes and
      triggers, but the tree does not surface them
- [ ] `pycryptodome` is a declared dependency but nothing imports it; either finish the feature it was
      meant for or drop the dependency
- [ ] Packaging script is x86_64 Linux only; no Windows or macOS build
- [ ] No automated tests

See the [open issues](https://github.com/Elouahabi-Naoufal/SQLiteExplorer/issues) for a full list of
proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create.
Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You
can also simply open an issue with the tag "enhancement". Don't forget to give the project a star!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Top contributors:

<a href="https://github.com/Elouahabi-Naoufal/SQLiteExplorer/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Elouahabi-Naoufal/SQLiteExplorer" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

This project is not licensed — all rights reserved.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Naoufal Elouahabi - [LinkedIn](https://www.linkedin.com/in/elouahabi-naoufal/) - elouahabi-naoufal1@gmail.com

Project Link: [https://github.com/Elouahabi-Naoufal/SQLiteExplorer](https://github.com/Elouahabi-Naoufal/SQLiteExplorer)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [SQLite](https://www.sqlite.org/) and [SQLCipher](https://www.zetetic.net/sqlcipher/)
* [PyQt6 / Riverbank Computing](https://www.riverbankcomputing.com/software/pyqt/)
* [PyInstaller](https://pyinstaller.org/)
* [AppImageKit](https://github.com/AppImage/AppImageKit)
* [Img Shields](https://shields.io)
* [Choose an Open Source License](https://choosealicense.com)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/Elouahabi-Naoufal/SQLiteExplorer.svg?style=for-the-badge
[contributors-url]: https://github.com/Elouahabi-Naoufal/SQLiteExplorer/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Elouahabi-Naoufal/SQLiteExplorer.svg?style=for-the-badge
[forks-url]: https://github.com/Elouahabi-Naoufal/SQLiteExplorer/network/members
[stars-shield]: https://img.shields.io/github/stars/Elouahabi-Naoufal/SQLiteExplorer.svg?style=for-the-badge
[stars-url]: https://github.com/Elouahabi-Naoufal/SQLiteExplorer/stargazers
[issues-shield]: https://img.shields.io/github/issues/Elouahabi-Naoufal/SQLiteExplorer.svg?style=for-the-badge
[issues-url]: https://github.com/Elouahabi-Naoufal/SQLiteExplorer/issues
[license-shield]: https://img.shields.io/badge/license-unlicensed-lightgrey?style=for-the-badge
[license-url]: https://github.com/Elouahabi-Naoufal/SQLiteExplorer
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/elouahabi-naoufal/
[Python.com]: https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[PyQt6.com]: https://img.shields.io/badge/PyQt6-2C7BB4?style=for-the-badge&logo=qt&logoColor=white
[PyQt6-url]: https://www.riverbankcomputing.com/software/pyqt/
[SQLite.com]: https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://www.sqlite.org/
[SQLCipher.com]: https://img.shields.io/badge/SQLCipher-0F80C0?style=for-the-badge
[SQLCipher-url]: https://www.zetetic.net/sqlcipher/
[Matplotlib.com]: https://img.shields.io/badge/matplotlib-11557C?style=for-the-badge&logo=python&logoColor=white
[Matplotlib-url]: https://matplotlib.org/
[pandas.com]: https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white
[pandas-url]: https://pandas.pydata.org/
[PyInstaller.com]: https://img.shields.io/badge/PyInstaller-3C1387?style=for-the-badge
[PyInstaller-url]: https://pyinstaller.org/
