from rest_framework import serializers
from backend.models import PC, Dados

class DadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dados
        fields = ['temperatura', 'uso_CPU', 'uso_RAM', 'data_recebimento']
        
    def to_representation(self, instance):
        data = instance.data_recebimento.strftime('%d/%m/%Y %H:%M:%S')
        return {
            'temperatura': f"{instance.temperatura} ºC",
            'uso_CPU': f"{instance.uso_CPU} %",
            'uso_RAM': f"{instance.uso_RAM} %",
            'data_recebimento': data
        }

class PCSerializer(serializers.ModelSerializer):
    dados = DadosSerializer(many=True)

    class Meta:
        model = PC
        fields = ['user', 'power', 'dados']

    def create(self, validated_data):
        user = validated_data.pop('user')
        dados_data = validated_data.pop('dados')
        

        pc, created = PC.objects.get_or_create(user=user)

        for dado_data in dados_data:
            Dados.objects.create(pc=pc, **dado_data)

        return pc

class PCPowerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PC
        fields = ['power']

    def update(self, instance, validated_data):
        instance.power = validated_data.get('power', instance.power)
        instance.save()
        return instance