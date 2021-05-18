import os


def save_file(fid, data):
    file = open(_store_path() + "/files/" + str(fid), "wb")
    file.write(bytes(data))
    file.close()


def read_file(fid):
    file = open(_store_path() + "/files/" + str(fid), "rb")
    data = file.read()
    file.close()
    return list(data)


def persist_file_registry(registry):
    guarantee_files()
    max_uuid = running_file_uuid()
    registry_file = open(_store_path() + "/files/registry", "a")
    max = max_uuid
    for fid, (name, uid, image, length, chid) in registry.items():
        if fid > max_uuid:
            registry_file.write(str(fid) + "," + "\"" + name + "\"," + str(uid) + "," + str(image) + "," + str(length) +
                                "," + str(chid) + "\n")
            if fid > max:
                max = fid
    save_running_file_uuid(max)
    registry_file.close()


def read_file_registry():
    guarantee_files()
    registry = {}
    registry_file = open(_store_path() + "/files/registry", "r")
    for line in registry_file:
        fid_str, name, uid_str, image_str, length_str, chid_str = line.split(",")
        fid = int(fid_str)
        uid = int(uid_str)
        length = int(length_str)
        chid = int(chid_str.strip("\n"))
        image = False
        if image_str == "True":
            image = True
        name = name.strip("\"")
        registry[fid] = (name, uid, image, length, chid)
    return registry


def read_user_registry():
    guarantee_users()
    registry = {}
    registry_file = open(_store_path() + "/users/registry", "r")
    for line in registry_file:
        username, password, uid_str = line.split(",")
        username = username.strip("\"")
        password = password.strip("\"")
        uid = int(uid_str)
        registry[username] = (password, uid)
    return registry


def running_file_uuid():
    guarantee_files()
    files_uuid_path = _store_path() + "/files/uuid"
    uuid = open(files_uuid_path, "r")
    running_uuid = int(uuid.read())
    uuid.close()
    return running_uuid


def save_running_file_uuid(running_uuid):
    files_uuid_path = _store_path() + "/files/uuid"
    uuid = open(files_uuid_path, "w")
    uuid.write(str(running_uuid))
    uuid.close()


def running_user_uuid():
    guarantee_files()
    files_uuid_path = _store_path() + "/users/uuid"
    uuid = open(files_uuid_path, "r")
    running_uuid = int(uuid.read())
    uuid.close()
    return running_uuid


def save_running_user_uuid(running_uuid):
    files_uuid_path = _store_path() + "/users/uuid"
    uuid = open(files_uuid_path, "w")
    uuid.write(str(running_uuid))
    uuid.close()


def guarantee_complete_store():
    guarantee_store()
    guarantee_users()
    guarantee_files()


def guarantee_store():
    if not os.path.exists(_store_path()):
        os.mkdir(_store_path())


def guarantee_users():
    guarantee_store()
    users_path = _store_path() + "/users"
    if not os.path.exists(users_path):
        os.mkdir(users_path)
        open(users_path + "/registry", "w").close()
        uuid_path = users_path + "/uuid"
        uuid = open(uuid_path, "w")
        uuid.write("0")
        uuid.close()


def guarantee_files():
    guarantee_store()
    files_path = _store_path() + "/files"
    if not os.path.exists(files_path):
        os.mkdir(files_path)
        open(files_path + "/registry", "w").close()
        uuid_path = files_path + "/uuid"
        uuid = open(uuid_path, "w")
        uuid.write("0")
        uuid.close()


def persist_user_registry(registry):
    guarantee_users()
    max_uuid = running_user_uuid()
    registry_file = open(_store_path() + "/users/registry", "a")
    max = max_uuid
    for username, (password, uid) in registry.items():
        if uid > max_uuid:
            registry_file.write("\"" + str(username) + "\",\"" + password + "\"," + str(uid) + "\n")
            if uid > max:
                max = uid
    save_running_user_uuid(max)
    registry_file.close()


def _store_path():
    return _project_root() + "/.server_store"


def _project_root():
    return _parent_path(_parent_path(__file__))


def _parent_path(path):
    index = path.rfind(os.sep)
    return path[:index]
