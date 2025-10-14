from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, FloatField, IntegerField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, ValidationError
from app.models import Unit, Technique, Lab, User, Parameter, Provider, Result, Cycle


class UnitForm(FlaskForm):
    code = StringField('Codice Unità', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Descrizione', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Salva')

    def __init__(self, original_code=None, *args, **kwargs):
        super(UnitForm, self).__init__(*args, **kwargs)
        self.original_code = original_code

    def validate_code(self, field):
        if field.data != self.original_code:
            unit = Unit.query.filter_by(code=field.data).first()
            if unit:
                raise ValidationError('Questo codice unità esiste già.')


class TechniqueForm(FlaskForm):
    code = StringField('Codice Tecnica', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Nome Tecnica', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Salva')

    def __init__(self, original_code=None, *args, **kwargs):
        super(TechniqueForm, self).__init__(*args, **kwargs)
        self.original_code = original_code

    def validate_code(self, field):
        if field.data != self.original_code:
            technique = Technique.query.filter_by(code=field.data).first()
            if technique:
                raise ValidationError('Questo codice tecnica esiste già.')


class ParameterForm(FlaskForm):
    code = StringField('Codice Parametro', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Nome Parametro', validators=[DataRequired(), Length(min=1, max=200)])
    unit_code = SelectField('Unità di Misura', validators=[DataRequired()], coerce=str)
    technique_id = SelectField('Tecnica Analitica', validators=[Optional()], coerce=int)
    matrix = StringField('Matrice', validators=[Optional(), Length(max=100)])
    min_value = FloatField('Valore Minimo', validators=[Optional()])
    max_value = FloatField('Valore Massimo', validators=[Optional()])
    precision_digits = IntegerField('Cifre Decimali', validators=[Optional(), NumberRange(min=0, max=10)], default=2)
    description = TextAreaField('Descrizione', validators=[Optional()])
    active = BooleanField('Attivo', default=True)
    submit = SubmitField('Salva')

    def __init__(self, original_code=None, *args, **kwargs):
        super(ParameterForm, self).__init__(*args, **kwargs)
        self.original_code = original_code
        # Populate choices for select fields
        self.unit_code.choices = [('', 'Selecione uma unidade')] + [(u.code, f"{u.code} - {u.description}") for u in Unit.query.all()]
        self.technique_id.choices = [('', 'Selecione uma técnica')] + [(t.id, f"{t.name}") for t in Technique.query.all()]

    def validate_code(self, field):
        if field.data != self.original_code:
            parameter = Parameter.query.filter_by(code=field.data).first()
            if parameter:
                raise ValidationError('Este código de parâmetro já existe.')

    def validate_max_value(self, field):
        if field.data is not None and self.min_value.data is not None:
            if field.data <= self.min_value.data:
                raise ValidationError('O valor máximo deve ser maior que o valor mínimo.')


class LabForm(FlaskForm):
    code = StringField('Código do Laboratório', validators=[DataRequired(), Length(min=1, max=10)])
    name = StringField('Nome do Laboratório', validators=[DataRequired(), Length(min=1, max=100)])
    address = TextAreaField('Endereço', validators=[Optional(), Length(max=255)])
    contact_person = StringField('Pessoa de Contato', validators=[Optional(), Length(max=100)])
    contact_email = StringField('Email de Contato', validators=[Optional(), Length(max=100)])
    contact_phone = StringField('Telefone de Contato', validators=[Optional(), Length(max=20)])
    active = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar')

    def __init__(self, original_code=None, *args, **kwargs):
        super(LabForm, self).__init__(*args, **kwargs)
        self.original_code = original_code

    def validate_code(self, field):
        if field.data != self.original_code:
            lab = Lab.query.filter_by(code=field.data).first()
            if lab:
                raise ValidationError('Este código de laboratório já existe.')


class CycleForm(FlaskForm):
    code = StringField('Código do Ciclo', validators=[DataRequired(), Length(min=1, max=20)])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=255)])
    coordinator_id = SelectField('Coordenador', validators=[DataRequired()], coerce=int)
    lab_code = SelectField('Laboratório', validators=[DataRequired()], coerce=str)
    active = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar')

    def __init__(self, original_code=None, *args, **kwargs):
        super(CycleForm, self).__init__(*args, **kwargs)
        self.original_code = original_code
        # Populate choices for select fields
        self.coordinator_id.choices = [('', 'Selecione um coordenador')] + [(u.id, f"{u.name} ({u.email})") for u in User.query.filter_by(active=True).all()]
        self.lab_code.choices = [('', 'Selecione um laboratório')] + [(lab.code, f"{lab.code} - {lab.name}") for lab in Lab.query.filter_by(active=True).all()]

    def validate_code(self, field):
        if field.data != self.original_code:
            from app.models import Cycle
            cycle = Cycle.query.filter_by(code=field.data).first()
            if cycle:
                raise ValidationError('Este código de ciclo já existe.')


class UserForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(min=1, max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(min=1, max=120)])
    role_id = SelectField('Função', validators=[DataRequired()], coerce=int)
    lab_code = SelectField('Laboratório', validators=[Optional()], coerce=str)
    active = BooleanField('Ativo', default=True)
    submit = SubmitField('Salvar')

    def __init__(self, original_id=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.original_id = original_id
        # Populate choices for select fields
        from app.models import Role
        self.role_id.choices = [('', 'Selecione uma função')] + [(r.id, r.name) for r in Role.query.all()]
        self.lab_code.choices = [('', 'Nenhum laboratório')] + [(lab.code, f"{lab.code} - {lab.name}") for lab in Lab.query.filter_by(active=True).all()]

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user and user.id != self.original_id:
            raise ValidationError('Este email já está em uso.')


# Form for bulk operations
class BulkActionForm(FlaskForm):
    action = SelectField('Ação', validators=[DataRequired()], 
                        choices=[('activate', 'Ativar Selecionados'), 
                                ('deactivate', 'Desativar Selecionados'),
                                ('delete', 'Excluir Selecionados')])
    submit = SubmitField('Executar')


# Search form for filtering lists
class SearchForm(FlaskForm):
    query = StringField('Buscar', validators=[Optional(), Length(max=100)])
    active_filter = SelectField('Status', choices=[('all', 'Todos'), ('active', 'Ativos'), ('inactive', 'Inativos')], default='all')
    submit = SubmitField('Filtrar')


class ProviderForm(FlaskForm):
    code = StringField('Codice Fornitore', validators=[DataRequired(), Length(min=1, max=20)])
    name = StringField('Nome Fornitore', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Salva')

    def __init__(self, original_code=None, *args, **kwargs):
        super(ProviderForm, self).__init__(*args, **kwargs)
        self.original_code = original_code

    def validate_code(self, field):
        if field.data != self.original_code:
            provider = Provider.query.filter_by(code=field.data).first()
            if provider:
                raise ValidationError('Questo codice fornitore esiste già.')


class ChartsForm(FlaskForm):
    """Form completo per grafici - 100% Python, no JavaScript"""
    parameters = SelectMultipleField('Parametri', coerce=str)
    techniques = SelectMultipleField('Tecniche', coerce=str) 
    cycles = SelectMultipleField('Cicli', coerce=str)
    days = SelectField('Periodo', 
                      choices=[
                          ('7', '7 giorni'),
                          ('30', '30 giorni'),
                          ('60', '60 giorni'),
                          ('90', '90 giorni')
                      ], 
                      default='30')
    submit = SubmitField('Aggiorna Grafico')
    
    def __init__(self, lab_code=None, *args, **kwargs):
        super(ChartsForm, self).__init__(*args, **kwargs)
        self.lab_code = lab_code
        self.populate_choices()
    
    def populate_choices(self):
        """Popola le scelte dai dati del database"""
        if not self.lab_code:
            return
            
        from app import db
        
        try:
            # Parametri disponibili per questo lab
            params = db.session.query(Result.parameter_code, Parameter.name)\
                .join(Parameter, Result.parameter_code == Parameter.code)\
                .filter(Result.lab_code == self.lab_code)\
                .distinct().all()
            
            self.parameters.choices = [(p[0], f"{p[0]} - {p[1] or p[0]}") for p in params]
            
            # Tecniche disponibili
            techs = db.session.query(Result.technique_code, Technique.name)\
                .join(Technique, Result.technique_code == Technique.code, isouter=True)\
                .filter(Result.lab_code == self.lab_code, Result.technique_code.isnot(None))\
                .distinct().all()
            
            self.techniques.choices = [(t[0], f"{t[0]} - {t[1] or t[0]}") for t in techs]
            
            # Cicli disponibili  
            cycles = db.session.query(Result.cycle_code, Cycle.name)\
                .join(Cycle, Result.cycle_code == Cycle.code)\
                .filter(Result.lab_code == self.lab_code)\
                .distinct().all()
                
            self.cycles.choices = [(c[0], f"{c[0]} - {c[1] or c[0]}") for c in cycles]
            
        except Exception as e:
            print(f"Errore nel caricamento scelte: {e}")
            # Fallback vuoto
            self.parameters.choices = []
            self.techniques.choices = []
            self.cycles.choices = []

class ChartFiltersForm(FlaskForm):
    """Form per i filtri dei grafici di controllo - Versione Semplificata"""
    days = SelectField('Periodo Temporale', choices=[
        ('7', 'Ultimi 7 giorni'),
        ('30', 'Ultimi 30 giorni'),
        ('90', 'Ultimi 90 giorni'),
        ('365', 'Ultimo anno'),
        ('', 'Tutti i dati')
    ], default='30', validators=[Optional()])
    submit = SubmitField('Aggiorna Grafico')

    def __init__(self, lab_code=None, *args, **kwargs):
        super(ChartFiltersForm, self).__init__(*args, **kwargs)
        self.lab_code = lab_code