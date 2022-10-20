from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from apps.company.models import CompanyPresent, CompanyPresentDetails, CompanyPresentDocuments, CompanyPresentTeamMember
from apps.company.serializer import CompanyPresentDetailsSerializer, CompanyPresentDocumentsSerializer, \
    CompanyPresentTeamMemberSerializer
from utils.serializers import get_model_fields

"""
Present Details
"""


class PresentDetailsEmbededUpdateListSerializer(serializers.ListSerializer):

    def bulkupdate(self, validated_data):
        for item in validated_data:
            CompanyPresentDetails.objects.filter(id=item.pop('id')).update(**item)
        return validated_data


class PresentDetailsEmbededUpdateUpdateSerializer(FlexFieldsModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = CompanyPresentDetails
        fields = "__all__"
        list_serializer_class = PresentDetailsEmbededUpdateListSerializer


class PresentDetailsEmbededBuklkUpdateSerializer(serializers.Serializer):
    def save(self, validated_data, instance_pk):
        deleted_items = validated_data.get('deleted_items')
        created_item = validated_data.get('created_items')
        update_item = validated_data.get('updated_items')

        if deleted_items:
            CompanyPresentDetails.objects.filter(pk__in=[item.pk for item in deleted_items]).delete()
        if created_item:
            item_set_serializer = self.fields['created_items']
            for item in created_item:
                item['company'] = instance_pk
            item_set_serializer.create(created_item)
        if update_item:
            item_set_serializer = self.fields['updated_items']
            item_set_serializer.bulkupdate(update_item)
        return validated_data

    deleted_items = serializers.PrimaryKeyRelatedField(required=False, many=True,
                                                       queryset=CompanyPresentDetails.objects.all(),
                                                       allow_null=False,
                                                       allow_empty=False
                                                       )
    updated_items = PresentDetailsEmbededUpdateUpdateSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )
    created_items = CompanyPresentDetailsSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )


"""
Present Document
"""


class PresentDocumentEmbededUpdateListSerializer(serializers.ListSerializer):

    def bulkupdate(self, validated_data):
        for item in validated_data:
            CompanyPresentDocuments.objects.filter(id=item.pop('id')).update(**item)
        return validated_data


class PresentDocumentEmbededUpdateUpdateSerializer(FlexFieldsModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = CompanyPresentDocuments
        fields = "__all__"
        list_serializer_class = PresentDocumentEmbededUpdateListSerializer


class PresentDocumentEmbededBulkUpdateSerializer(serializers.Serializer):
    def save(self, validated_data, instance_pk):
        deleted_items = validated_data.get('deleted_items')
        created_item = validated_data.get('created_items')
        update_item = validated_data.get('updated_items')

        if deleted_items:
            CompanyPresentDocuments.objects.filter(pk__in=[item.pk for item in deleted_items]).delete()
        if created_item:
            item_set_serializer = self.fields['created_items']
            for item in created_item:
                item['company'] = instance_pk
            item_set_serializer.create(created_item)
        if update_item:
            item_set_serializer = self.fields['updated_items']
            item_set_serializer.bulkupdate(update_item)
        return validated_data

    deleted_items = serializers.PrimaryKeyRelatedField(required=False, many=True,
                                                       queryset=CompanyPresentDocuments.objects.all(),
                                                       allow_null=False,
                                                       allow_empty=False
                                                       )
    updated_items = PresentDocumentEmbededUpdateUpdateSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )
    created_items = CompanyPresentDocumentsSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )


"""
Team member updated 
"""


class CompanyPresentTeamMemberEmbededUpdateListSerializer(serializers.ListSerializer):

    def bulkupdate(self, validated_data):
        for item in validated_data:
            CompanyPresentTeamMember.objects.filter(id=item.pop('id')).update(**item)
        return validated_data


class CompanyPresentTeamMemberEmbededUpdateUpdateSerializer(FlexFieldsModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = CompanyPresentTeamMember
        fields = "__all__"
        list_serializer_class = CompanyPresentTeamMemberEmbededUpdateListSerializer


class CompanyPresentTeamMemberEmbededBulkUpdateSerializer(serializers.Serializer):
    def save(self, validated_data, instance_pk):
        deleted_items = validated_data.get('deleted_items')
        created_item = validated_data.get('created_items')
        update_item = validated_data.get('updated_items')

        if deleted_items:
            CompanyPresentTeamMember.objects.filter(pk__in=[item.pk for item in deleted_items]).delete()
        if created_item:
            item_set_serializer = self.fields['created_items']
            for item in created_item:
                item['company'] = instance_pk
            item_set_serializer.create(created_item)
        if update_item:
            item_set_serializer = self.fields['updated_items']
            item_set_serializer.bulkupdate(update_item)
        return validated_data

    deleted_items = serializers.PrimaryKeyRelatedField(required=False, many=True,
                                                       queryset=CompanyPresentTeamMember.objects.all(),
                                                       allow_null=False,
                                                       allow_empty=False
                                                       )
    updated_items = CompanyPresentTeamMemberEmbededUpdateUpdateSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )
    created_items = CompanyPresentTeamMemberSerializer(
        many=True,
        allow_null=False,
        allow_empty=False,
        required=False
    )


"""
Bulk Updated
"""


class CompanyPresentUpdateSerializer(FlexFieldsModelSerializer):
    present_details = PresentDetailsEmbededBuklkUpdateSerializer(many=False, required=False, allow_null=False,
                                                                 write_only=True)

    present_document = PresentDocumentEmbededBulkUpdateSerializer(many=False, required=False, allow_null=False,
                                                                  write_only=True)

    present_team_member = CompanyPresentTeamMemberEmbededBulkUpdateSerializer(many=False, required=False,
                                                                              allow_null=False,
                                                                              write_only=True)

    def update(self, instance, validated_data):
        present_details = validated_data.pop('present_details', None)
        present_document = validated_data.pop('present_document', None)
        present_team_member = validated_data.pop('present_team_member', None)
        instance_pk = super().update(instance, validated_data)
        if present_details:
            present_details_serializer = self.fields['present_details']
            present_details_serializer.save(validated_data=present_details, instance_pk=instance_pk)
        if present_document:
            present_document_serializer = self.fields['present_document']
            present_document_serializer.save(validated_data=present_document, instance_pk=instance_pk)
        if present_team_member:
            present_team_member_serializer = self.fields['present_team_member']
            present_team_member_serializer.save(validated_data=present_team_member, instance_pk=instance_pk)
        return validated_data

    class Meta:
        model = CompanyPresent
        fields = get_model_fields(CompanyPresent) + ('present_details', 'present_document','present_team_member')
        read_only_fields = ['company', 'status', 'is_trending']
