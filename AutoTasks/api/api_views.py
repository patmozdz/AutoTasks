from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from twilio.twiml.messaging_response import MessagingResponse


@api_view(['POST'])
def receive_sms_from_twilio(request):
    body = request.POST.get('Body', None)
    phone = request.POST.get('From', None)

    if not body or not phone:
        return Response({"error": "Invalid data."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, phone=phone)
    if user is not None:
        resp = MessagingResponse()
        resp.message("Hello, you are already registered.")
        # Proceed to do chatgpt stuff (remove you are already registered message)
    else:
        # Handle unauthenticated user
        resp = MessagingResponse()
        resp.message("You are not registered.")

    return Response(str(resp), status=status.HTTP_200_OK, content_type='text/xml')


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def upload_file(request):
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    file_instance = File.objects.create(user=request.user, file_object=uploaded_file)
    full_process.delay(file_instance.id)

    return Response({"message": "File uploaded successfully"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def user_notes(request):
    notes = Note.objects.filter(user=request.user)
    serializer = NoteSerializer(notes, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def user_files(request):
    status = request.GET.get('status', None)
    user = request.user

    if status:
        status_list = status.split(',')
        files = File.objects.filter(user=user, status__in=status_list)
    else:
        files = File.objects.filter(user=user)

    serializer = FileSerializer(files, many=True)

    return Response(serializer.data)


@api_view(['DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def delete_note(request, note_id):
    try:
        note = Note.objects.get(pk=note_id, user=request.user)
    except Note.DoesNotExist:
        return Response({"error": "Note not found."}, status=status.HTTP_404_NOT_FOUND)

    note.delete()

    return Response({"message": "Note deleted successfully."}, status=status.HTTP_200_OK)
