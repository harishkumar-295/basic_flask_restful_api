from flask import Flask
from flask_restful import Api,Resource,reqparse,abort,fields,marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class VideoModel(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    views = db.Column(db.Integer,nullable=False)
    likes = db.Column(db.Integer,nullable=False)
    
    def __repr__(self) -> str:
        return f"Video(name:{self.name}, views:{self.views}, likes:{self.likes})"

db.create_all()  # execute this only once and delete it


video_put_args = reqparse.RequestParser()

video_put_args.add_argument('name', type=str, help="name of video",required = True)
video_put_args.add_argument('views', type=int, help="views of video",required = True)
video_put_args.add_argument('likes', type=int, help="likes of video",required = True)

video_update_args = reqparse.RequestParser()

video_update_args.add_argument('name', type=str, help="name of video")
video_update_args.add_argument('views', type=int, help="views of video")
video_update_args.add_argument('likes', type=int, help="likes of video")

videos = {}

resource_fields = {
    "id":fields.Integer,
    "names":fields.String,
    "views":fields.Integer,
    "likes":fields.Integer,
}

def abort_if_video_id_doesnt_exist(video_id):
    if video_id not in videos:
        abort(404,message = "Couldn't find video...")

def abort_if_video_with_id_already_exists(video_id):
    if video_id in videos:
        abort(409,message="Video with id already exists...")

class Video(Resource):
    @marshal_with(resource_fields)
    def get(self,video_id):
        # abort_if_video_id_doesnt_exist(video_id)
        result = VideoModel.query.filter_by(id=video_id).first() # here result will return an instance of VideoModel class so it need's to be serialized
        if not result:
            abort(404,message = "Couldn't find video with id")
        return videos[video_id]
    
    @marshal_with(resource_fields)
    def put(self,video_id):
        # abort_if_video_with_id_already_exists(video_id)
        # args = video_put_args.parse_args()
        # videos[video_id] = args
        args = video_put_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if result:
            abort(409,message="Video already exists")
        video = VideoModel(id = video_id, name = args['name'],likes = args['likes'],views = args['views'])
        db.session.add(video)
        db.session.commit()
        # return videos[video_id],201
        return video,201
    
    @marshal_with(resource_fields)
    def patch(self,video_id):
        args = video_update_args.parse_args()
        result = VideoModel.query.filter_by(id=video_id).first()
        if not result:
            abort(404,message = "Couldn't find video with id")
        if args['name']:
            result.name = args['name']
        if args['views']:
            result.views = args['views']
        if args['likes']:
            result.likes = args['likes']
            
        db.session.commit()
        
        return result
    
    def delete(self,video_id):
        abort_if_video_id_doesnt_exist(video_id)
        del videos[video_id]
        return "deleted",204
    
api.add_resource(Video,"/video/<int:video_id>")

# names = {
#          "harish":{
#                    "age":24,
#                    "gender":"male"
#                    },
#          "chiran":{
#                    "age":20,
#                    "gender":"male"
#          }
#          }

# class HelloWorld(Resource):
#     def get(self,name):
#         return names[name]

# api.add_resource(HelloWorld,"/helloworld/<string:name>")

if __name__ == "__main__":
    app.run(debug=True)