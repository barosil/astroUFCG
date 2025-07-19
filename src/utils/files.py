from pathlib import Path


def get_path():
    import ipynbname
    from IPython import get_ipython

    ip = get_ipython()
    path = None
    if "__vsc_ipynb_file__" in ip.user_ns:
        path = Path(ip.user_ns["__vsc_ipynb_file__"])
    elif __file__ is not None:
        path = Path(__file__)
    else:
        path = Path(ipynbname.path())
    return path


def get_paths():
    package_name = "astroufcg"
    my_path = get_path()
    _my_path = my_path
    idx = str(my_path).lower().find(package_name)
    my_path = Path(str(my_path)[idx:])
    my_folder = my_path.parent
    _root = [
        (_idx, folder)
        for _idx, folder in enumerate(list(my_path.parents))
        if package_name in str(folder).lower().split("/")
    ][-1]

    idx = str(_root[1]).lower().find(package_name)

    dir = Path(str(list(_my_path.parents)[_root[0]]))
    root = Path(str(_root[1])[idx:])
    data_folder = Path(root / "data")
    notebooks_folder = Path(root / "notebooks")
    temp_folder = Path(root / "temp")
    content_folder = Path(root / "content")
    _folder = my_folder
    paths = []
    _path = None
    prefix = ""
    for target in [data_folder, notebooks_folder, temp_folder, content_folder]:
        while _path is None:
            try:
                _path = target.relative_to(_folder)
                prefix = prefix + "../"
                if _path:
                    paths.append((prefix + str(_path)))
                    _path = None
                    prefix = ""
                    break
            except ValueError:
                _folder = _folder.parent
                _path = None
                pass

    if paths is not None:
        path_dict = {
            "data_folder": Path(paths[0]),
            "notebooks_folder": Path(paths[1]) if len(paths) > 1 else None,
            "temp_folder": Path(paths[2]) if len(paths) > 2 else None,
            "content_folder": Path(paths[3]) if len(paths) > 3 else None,
            "my_path": my_path,
            "root": root,
            "diretorio": dir,
        }
    return path_dict
