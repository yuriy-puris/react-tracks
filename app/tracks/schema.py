import graphene
from graphene_django import DjangoObjectType


from .models import Track, Like
from users.schema import UserType

class TrackType(DjangoObjectType):
    class Meta:
        model = Track

class Query(graphene.ObjectType):
    
    tracks = graphene.List(TrackType)

    def return_tracks(self, info):
        return Track.objects.all()

class CreateTrack(graphene.Mutation):

    track = graphene.Field(TrackType)

    class Arguments:
        title = graphene.String()
        description = graphene.String()
        url = graphene.String()

    def mutate(self, info, title, description, url):
        user = info.context.user

        if user.is_anonymous:
            raise Exception('Log in not add')

        track = Track(title=title, description=description, url=url, posted_by=user)
        track.save()
        return CreateTrack(track=track)

class UpdateTrack(graphene.Mutation):

    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        url = graphene.String(required=True)

    def mutate(self, info, track_id, title, description, url):
        user = info.context.user
        track = Track.objects.get(id=track_id)

        if track.posted_by != user:
            raise Exception('Not permitted to update this track')

        track.title=title
        track.description=description
        track.url=url
        track.save()
        return UpdateTrack(track=track)

class DeleteTrack(graphene.Mutation):

    track_id = graphene.Int()

    class Arguments:
        track_id = graphene.Int()

    def mutate(self, info, track_id):
        user = info.context.user
        track = Track.objects.get(id=track_id)

        if track.posted_by != user:
            raise Exception('Not permitted to delete')

        track.delete()
        return DeleteTrack(track_id=track_id)

class CreateLike(graphene.Mutation):
    user = graphene.Field(UserType)
    track = graphene.Field(TrackType)

    class Arguments:
        track_id = graphene.Int(required=True)

    def mutate(self, info, track_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Log in to create like")

        track = Track.objects.get(id=track_id)
        if not track:
            raise Exception('Can not find track')

        Like.objects.create(
            user=user,
            track=track
        )

        return CreateLike(user=user, track=track)

class Mutation(graphene.ObjectType):
    create_track = CreateTrack.Field()
    update_track = UpdateTrack.Field()
    delete_track = DeleteTrack.Field()
    create_like = CreateLike.Field()