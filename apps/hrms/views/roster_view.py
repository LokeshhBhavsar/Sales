from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.authentication import JWTAuthentication
from apps.hrms.models.roster import Roster, RosterAssignment
from apps.hrms.serializers.roster_serializer import (
    RosterAssignmentUpdateSerializer,
    RosterEditSerializer,
    RosterSerializer,
)
from apps.hrms.services.roster_service import RosterService, _actor_name


class RosterListCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = RosterService.active_rosters()
        return Response({"success": True, "count": queryset.count(), "data": RosterSerializer(queryset, many=True).data})

    def post(self, request):
        serializer = RosterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        actor = _actor_name(request.user)
        try:
            roster = serializer.save(created_by_name=actor, updated_by_name=actor)
        except IntegrityError:
            return Response({"success": False, "message": "An active roster with this name and date range already exists for the selected plant."}, status=status.HTTP_409_CONFLICT)
        return Response({"success": True, "message": "Roster created successfully.", "data": RosterSerializer(roster).data}, status=status.HTTP_201_CREATED)


class RosterDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get(roster_id):
        return Roster.objects.select_related("company", "plant", "department").get(pk=roster_id, is_deleted=False)

    def patch(self, request, roster_id):
        try:
            roster = self._get(roster_id)
        except Roster.DoesNotExist:
            return Response({"success": False, "message": "Roster not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RosterEditSerializer(roster, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            roster = serializer.save(updated_by_name=_actor_name(request.user))
        except IntegrityError:
            return Response({"success": False, "message": "An active roster with this name and date range already exists."}, status=status.HTTP_409_CONFLICT)
        return Response({"success": True, "message": "Roster updated successfully.", "data": RosterSerializer(roster).data})

    @transaction.atomic
    def delete(self, request, roster_id):
        try:
            roster = self._get(roster_id)
        except Roster.DoesNotExist:
            return Response({"success": False, "message": "Roster not found."}, status=status.HTTP_404_NOT_FOUND)
        roster.is_deleted = True
        roster.updated_by_name = _actor_name(request.user)
        roster.save(update_fields=["is_deleted", "updated_by_name", "updated_at"])
        return Response({"success": True, "message": "Roster deleted successfully."}, status=status.HTTP_200_OK)


class RosterAssignView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get(roster_id):
        return Roster.objects.select_related("company", "plant", "department").get(pk=roster_id, is_deleted=False)

    def get(self, request, roster_id):
        try:
            roster = self._get(roster_id)
        except Roster.DoesNotExist:
            return Response({"success": False, "message": "Roster not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"success": True, "data": RosterService.assignment_grid(roster)})

    def post(self, request, roster_id):
        try:
            roster = self._get(roster_id)
        except Roster.DoesNotExist:
            return Response({"success": False, "message": "Roster not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            created = RosterService.generate_assignments(roster, request.data, request.user)
        except ValidationError:
            raise
        except IntegrityError:
            return Response({"success": False, "message": "Duplicate roster assignments are not allowed."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success": True, "message": "Roster assignments generated successfully.", "created_assignments": created}, status=status.HTTP_201_CREATED)


class RosterAssignmentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def _get(assignment_id):
        return RosterAssignment.objects.select_related("roster", "shift").get(pk=assignment_id, is_deleted=False, roster__is_deleted=False)

    def patch(self, request, assignment_id):
        try:
            assignment = self._get(assignment_id)
        except RosterAssignment.DoesNotExist:
            return Response({"success": False, "message": "Roster assignment not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RosterAssignmentUpdateSerializer(assignment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by_name=_actor_name(request.user))
        data = next(
            item for item in RosterService.assignment_grid(assignment.roster)["assignments"]
            if item["id"] == str(assignment.id)
        )
        return Response({"success": True, "message": "Roster assignment updated successfully.", "data": data})

    @transaction.atomic
    def delete(self, request, assignment_id):
        try:
            assignment = self._get(assignment_id)
        except RosterAssignment.DoesNotExist:
            return Response({"success": False, "message": "Roster assignment not found."}, status=status.HTTP_404_NOT_FOUND)
        assignment.is_deleted = True
        assignment.updated_by_name = _actor_name(request.user)
        assignment.save(update_fields=["is_deleted", "updated_by_name", "updated_at"])
        return Response({"success": True, "message": "Roster assignment deleted successfully."}, status=status.HTTP_200_OK)
