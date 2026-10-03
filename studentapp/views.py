from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

class StudentProfileViewSet(viewsets.ModelViewSet): 
    serializer_class = StudentProfileSerializer 
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self): 
        return Student.objects.filter(user=self.request.user)
    
    def get_object(self):
        return Student.objects.get(user = self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Documents.objects.filter(student__user = self.request.user)
    
    def perform_create(self, serializer):
        student = Student.objects.get(user=self.request.user)
        document = serializer.save(student=student)

        from .rag.ingestion import ingest_document

        result = ingest_document(document)

        if result["status"] == "failed":

            document.delete()

            raise serializers.ValidationError(
                result["message"]
            )
        
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def conversation_ask(request):

    conversation_id = request.data.get("conversation_id")
    question = request.data.get("question")

    

    if not question:
        return Response(
            {"error": "Question is required"},
            status=400
        )

    if not conversation_id:
        return Response(
            {"error": "conversation_id is required"},
            status=400
        )

    

    try:

        conversation = Conversation.objects.get(
            id=conversation_id,
            student__user=request.user
        )

    except Conversation.DoesNotExist:

        return Response(
            {"error": "Conversation not found"},
            status=404
        )

    
    messages = conversation.messages.order_by(
        "created_at"
    )

    history = []

    for message in messages:

        history.append({
            "role": message.role,
            "content": message.content
        })

    

    Message.objects.create(
        conversation=conversation,
        role="user",
        content=question
    )

    

    try:

        from .rag.conversation_pipeline import (
            ask_conversation
        )

        result = ask_conversation(
            question=question,
            user=request.user,
            history=history
        )

    except Exception as e:

        print(
            "CONVERSATION ERROR:",
            repr(e)
        )

        return Response(
            {"error": str(e)},
            status=500
        )

    

    Message.objects.create(
        conversation=conversation,
        role="assistant",
        content=result["answer"]
    )

    

    return Response({
        "conversation_id": conversation.id,
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "confidence": result.get("confidence", "")
    })

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_conversation(request):

    conversation = Conversation.objects.create(
        student=request.user.profile,
        title="New Conversation"
    )

    return Response({
        "conversation_id": conversation.id,
        "title": conversation.title
    }, status=201)