from routes.settings.settings_upload import UploadUsersFile, UploadPostsFile, UploadCommentsFile
from routes.settings.settings_update import *


def add_settings_routes(api):
    # Upload
    api.add_resource(UploadUsersFile, '/upload/users')
    api.add_resource(UploadPostsFile, '/upload/posts')
    api.add_resource(UploadCommentsFile, '/upload/comments')

    # Update
    api.add_resource(Info, '/info')
    api.add_resource(Status, '/status')
    api.add_resource(GetContentNotTagged, '/content/nottagged')
    api.add_resource(HardUpdate, '/hardUpdate')
    api.add_resource(HardUpdateFromEdgeRyders, '/hardUpdateFromEdgeRyders')
    api.add_resource(HardUpdateFromEdgeRydersDiscourse, '/hardUpdateFromEdgeRydersDiscourse')
    api.add_resource(UpdateFromEdgeRyders, '/UpdateFromEdgeRyders')
    api.add_resource(Update, '/update')
    api.add_resource(UpdateUsers, '/update/users')
    api.add_resource(UpdatePosts, '/update/posts')
    api.add_resource(UpdateComments, '/update/comments')
    api.add_resource(UpdateTags, '/update/tags')
    api.add_resource(UpdateAnnotations, '/update/annotations')
