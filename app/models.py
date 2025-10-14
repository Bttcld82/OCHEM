# app/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# ===========================
# TABELLE CORE
# ===========================

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    accepted_disclaimer_at = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)  # Campo per privilegi amministratore
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lab_roles = db.relationship('UserLabRole', back_populates='user', cascade='all, delete-orphan')
    uploads = db.relationship('UploadFile', back_populates='uploader')

    @property
    def name(self):
        """Nome completo dell'utente"""
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        """Imposta la password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la password"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        """Verifica se l'utente ha un ruolo globale"""
        if role_name == "admin":
            return self.is_admin or self.email.startswith("admin")  # Compatibilità con implementazione precedente
        return False

    def has_lab_role(self, lab_code, role_name):
        """Verifica se l'utente ha un ruolo specifico per un laboratorio"""
        for lab_role in self.lab_roles:
            if (lab_role.lab.code == lab_code and 
                lab_role.role.name == role_name):
                return True
        return False

    def get_lab_roles(self, lab_code):
        """Ottieni tutti i ruoli dell'utente per un laboratorio"""
        return [lr.role.name for lr in self.lab_roles if lr.lab.code == lab_code]
    
    def get_labs_count(self):
        """Ottieni il numero di laboratori a cui l'utente è associato"""
        return len(set(lr.lab_id for lr in self.lab_roles))
    
    def has_lab_min_role(self, lab_code, min_role):
        """Verifica se l'utente ha almeno il ruolo minimo per un laboratorio"""
        if self.has_role("admin"):
            return True
        
        role_hierarchy = {"owner_lab": 3, "analyst": 2, "viewer": 1}
        min_level = role_hierarchy.get(min_role, 0)
        
        for lab_role in self.lab_roles:
            if (lab_role.lab.code == lab_code and 
                role_hierarchy.get(lab_role.role.name, 0) >= min_level):
                return True
        
        return False

class Lab(db.Model):
    __tablename__ = 'lab'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(30), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #relazioni
    user_roles = db.relationship('UserLabRole', back_populates='lab', cascade='all, delete-orphan')
    participations = db.relationship('LabParticipation', back_populates='lab', cascade='all, delete-orphan')
    results = db.relationship('Result', back_populates='lab', cascade='all, delete-orphan')
    uploads = db.relationship('UploadFile', back_populates='lab', cascade='all, delete-orphan')
    stats = db.relationship('PtStats', back_populates='lab', primaryjoin='Lab.code==PtStats.lab_code')
    invites = db.relationship('InviteToken', back_populates='lab', cascade='all, delete-orphan', primaryjoin='Lab.code==InviteToken.lab_code', foreign_keys='InviteToken.lab_code')

class Role(db.Model):
    __tablename__ = 'role'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    #relazioni
    user_roles = db.relationship('UserLabRole', back_populates='role', cascade='all, delete-orphan')

class UserLabRole(db.Model):
    __tablename__ = 'user_lab_role'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'lab_id', name='uq_user_lab'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey('lab.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    user = db.relationship('User', back_populates='lab_roles')
    lab = db.relationship('Lab', back_populates='user_roles')
    role = db.relationship('Role', back_populates='user_roles')

# ===========================
# TABELLE ANAGRAFICHE
# ===========================

class Unit(db.Model):
    __tablename__ = 'unit'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    parameters = db.relationship('Parameter', back_populates='unit', primaryjoin='Unit.code==Parameter.unit_code')

class Matrix(db.Model):
    __tablename__ = 'matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Parameter(db.Model):
    __tablename__ = 'parameter'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    unit_code = db.Column(db.String(20), db.ForeignKey('unit.code'), nullable=False)
    technique_id = db.Column(db.Integer, db.ForeignKey('technique.id'), nullable=True)
    matrix = db.Column(db.String(100), nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)
    precision_digits = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    unit = db.relationship('Unit', back_populates='parameters', primaryjoin='Unit.code==Parameter.unit_code')
    technique = db.relationship('Technique', backref='parameters')
    cycle_parameters = db.relationship('CycleParameter', back_populates='parameter', primaryjoin='Parameter.code==CycleParameter.parameter_code', cascade='all, delete-orphan')
    results = db.relationship('Result', back_populates='parameter', primaryjoin='Parameter.code==Result.parameter_code')
    stats = db.relationship('PtStats', back_populates='parameter', primaryjoin='Parameter.code==PtStats.parameter_code')

class Technique(db.Model):
    __tablename__ = 'technique'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    results = db.relationship('Result', back_populates='technique', primaryjoin='Technique.code==Result.technique_code')

class Provider(db.Model):
    __tablename__ = 'provider'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    cycles = db.relationship('Cycle', back_populates='provider')

# ===========================
# TABELLE DOCUMENTI
# ===========================

class DocFile(db.Model):
    __tablename__ = 'doc_file'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relazioni
    cycles = db.relationship('Cycle', back_populates='doc_file')
    cycle_links = db.relationship('CycleDoc', back_populates='doc', cascade='all, delete-orphan')

class CycleDoc(db.Model):
    __tablename__ = 'cycle_doc'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_code = db.Column(db.String(20), db.ForeignKey('cycle.code'), nullable=False)
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_file.id'), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relazioni
    doc = db.relationship('DocFile', back_populates='cycle_links')
    cycle = db.relationship('Cycle', back_populates='docs', primaryjoin='Cycle.code==CycleDoc.cycle_code')

# ===========================
# TABELLE CICLI
# ===========================

class Cycle(db.Model):
    __tablename__ = 'cycle'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')
    doc_id = db.Column(db.Integer, db.ForeignKey('doc_file.id'), nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=True)
    provider = db.relationship('Provider', back_populates='cycles')
    doc_file = db.relationship('DocFile', back_populates='cycles', uselist=False)
    docs = db.relationship('CycleDoc', back_populates='cycle', cascade='all, delete-orphan', primaryjoin='Cycle.code==CycleDoc.cycle_code')
    parameters = db.relationship('CycleParameter', back_populates='cycle', primaryjoin='Cycle.code==CycleParameter.cycle_code', cascade='all, delete-orphan')
    participants = db.relationship('LabParticipation', back_populates='cycle', cascade='all, delete-orphan', primaryjoin='Cycle.code==LabParticipation.cycle_code')
    results = db.relationship('Result', back_populates='cycle', cascade='all, delete-orphan', primaryjoin='Cycle.code==Result.cycle_code')
    stats = db.relationship('PtStats', back_populates='cycle', cascade='all, delete-orphan', primaryjoin='Cycle.code==PtStats.cycle_code')
    uploads = db.relationship('UploadFile', back_populates='cycle', cascade='all, delete-orphan', primaryjoin='Cycle.code==UploadFile.cycle_code')

class CycleParameter(db.Model):
    __tablename__ = 'cycle_parameter'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_code = db.Column(db.String(20), db.ForeignKey('cycle.code'), nullable=False)
    parameter_code = db.Column(db.String(20), db.ForeignKey('parameter.code'), nullable=False)
    xpt = db.Column(db.Numeric(18, 6), nullable=False)
    sigma_pt = db.Column(db.Numeric(18, 6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    cycle = db.relationship('Cycle', back_populates='parameters', primaryjoin='Cycle.code==CycleParameter.cycle_code')
    parameter = db.relationship('Parameter', back_populates='cycle_parameters', primaryjoin='Parameter.code==CycleParameter.parameter_code')

# ===========================
# TABELLE PARTECIPAZIONI
# ===========================

class LabParticipation(db.Model):
    __tablename__ = 'lab_participation'
    
    id = db.Column(db.Integer, primary_key=True)
    lab_code = db.Column(db.String(50), db.ForeignKey('lab.code'), nullable=False)
    cycle_code = db.Column(db.String(20), db.ForeignKey('cycle.code'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    lab= db.relationship('Lab', back_populates='participations', primaryjoin='Lab.code==LabParticipation.lab_code')
    cycle = db.relationship('Cycle', back_populates='participants', primaryjoin='Cycle.code==LabParticipation.cycle_code')
    result = db.relationship('Result', back_populates='lab_participation', primaryjoin='LabParticipation.id==Result.lab_participation_id', cascade='all, delete-orphan')

class Result(db.Model):
    __tablename__ = 'result'
    
    id = db.Column(db.Integer, primary_key=True)
    lab_code = db.Column(db.String(50), db.ForeignKey('lab.code'), nullable=False)
    cycle_code = db.Column(db.String(20), db.ForeignKey('cycle.code'), nullable=False)
    parameter_code = db.Column(db.String(20), db.ForeignKey('parameter.code'), nullable=False)
    technique_code = db.Column(db.String(20), db.ForeignKey('technique.code'), nullable=True)
    lab_participation_id = db.Column(db.Integer, db.ForeignKey('lab_participation.id'), nullable=True)
    measured_value = db.Column(db.Numeric(18, 6), nullable=False)
    uncertainty = db.Column(db.Numeric(18, 6), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    lab= db.relationship('Lab', back_populates='results', primaryjoin='Lab.code==Result.lab_code')
    cycle = db.relationship('Cycle', back_populates='results', primaryjoin='Cycle.code==Result.cycle_code')
    parameter = db.relationship('Parameter', back_populates='results', primaryjoin='Parameter.code==Result.parameter_code')
    technique = db.relationship('Technique', back_populates='results', primaryjoin='Technique.code==Result.technique_code')
    lab_participation = db.relationship('LabParticipation', back_populates='result')
    zscore= db.relationship('ZScore', back_populates='result', cascade='all, delete-orphan', uselist=False)
# ===========================
# TABELLE DERIVATI QC
# ===========================

class ZScore(db.Model):
    __tablename__ = 'z_score'
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    z = db.Column(db.Numeric(18, 6), nullable=False)
    sz2 = db.Column(db.Numeric(18, 6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relazioni
    result = db.relationship('Result', back_populates='zscore')

class PtStats(db.Model):
    __tablename__ = 'pt_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    cycle_code = db.Column(db.String(20), db.ForeignKey('cycle.code'), nullable=False)
    parameter_code = db.Column(db.String(20), db.ForeignKey('parameter.code'), nullable=False)
    lab_code = db.Column(db.String(50), db.ForeignKey('lab.code'), nullable=False)
    n_results = db.Column(db.Integer, nullable=False)
    mean_z = db.Column(db.Numeric(18, 6), nullable=True)
    rsz = db.Column(db.Numeric(18, 6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    # relazioni
    cycle = db.relationship('Cycle', back_populates='stats', primaryjoin='Cycle.code==PtStats.cycle_code')
    parameter = db.relationship('Parameter', back_populates='stats', primaryjoin='Parameter.code==PtStats.parameter_code')
    lab= db.relationship('Lab', back_populates='stats', primaryjoin='Lab.code==PtStats.lab_code')

class ControlChartConfig(db.Model):
    __tablename__ = 'control_chart_config'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chart_type = db.Column(db.String(50), nullable=False)
    center_line = db.Column(db.Numeric(18, 6), nullable=False)
    upper_control_limit = db.Column(db.Numeric(18, 6), nullable=False)
    lower_control_limit = db.Column(db.Numeric(18, 6), nullable=False)
    upper_warning_limit = db.Column(db.Numeric(18, 6), nullable=True)
    lower_warning_limit = db.Column(db.Numeric(18, 6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ===========================
# TABELLE AUDIT
# ===========================

class UploadFile(db.Model):
    __tablename__ = 'upload_file'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    lab_code = db.Column(db.String(50), db.ForeignKey('lab.code'), nullable=False)
    cycle_code = db.Column(db.String(20), db.ForeignKey('cycle.code'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')

    # relazioni
    lab = db.relationship('Lab', back_populates='uploads', primaryjoin='Lab.code==UploadFile.lab_code')
    cycle = db.relationship('Cycle', back_populates='uploads', primaryjoin='Cycle.code==UploadFile.cycle_code')
    uploader = db.relationship('User', back_populates='uploads')

class JobLog(db.Model):
    __tablename__ = 'job_log'
    
    id = db.Column(db.Integer, primary_key=True)
    job_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    details = db.Column(db.Text, nullable=True)

# ===========================
# TABELLE AUTENTICAZIONE E REGISTRAZIONE
# ===========================

class RegistrationRequest(db.Model):
    __tablename__ = 'registration_request'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=True)
    desired_lab_name = db.Column(db.String(100), nullable=True)
    target_lab_code = db.Column(db.String(20), nullable=True)
    desired_role = db.Column(db.String(20), nullable=False, default='owner_lab')
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='submitted', index=True)
    admin_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    decided_at = db.Column(db.DateTime, nullable=True)
    decided_by = db.Column(db.String(120), nullable=True)
    
    # Metodi di utilità
    @property
    def is_pending(self):
        return self.status in ['submitted', 'under_review']
    
    @property
    def is_decided(self):
        return self.status in ['approved', 'rejected']
    
    def approve(self, admin_email, admin_note=None):
        """Approva la richiesta di registrazione"""
        self.status = 'approved'
        self.decided_at = datetime.utcnow()
        self.decided_by = admin_email
        if admin_note:
            self.admin_note = admin_note
    
    def reject(self, admin_email, admin_note=None):
        """Rifiuta la richiesta di registrazione"""
        self.status = 'rejected'
        self.decided_at = datetime.utcnow()
        self.decided_by = admin_email
        if admin_note:
            self.admin_note = admin_note

class InviteToken(db.Model):
    __tablename__ = 'invite_token'
    
    id = db.Column(db.Integer, primary_key=True)
    lab_code = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)
    token = db.Column(db.String(96), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relazioni
    lab = db.relationship('Lab', back_populates='invites', primaryjoin='Lab.code==InviteToken.lab_code', foreign_keys='InviteToken.lab_code')
    
    @property
    def is_expired(self):
        """Verifica se il token è scaduto"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_used(self):
        """Verifica se il token è già stato usato"""
        return self.used_at is not None
    
    @property
    def is_valid(self):
        """Verifica se il token è ancora valido"""
        return not self.is_expired and not self.is_used
    
    def use_token(self):
        """Marca il token come utilizzato"""
        self.used_at = datetime.utcnow()
    
    @classmethod
    def create_invite(cls, lab_code, email, role, created_by, expires_in_days=7):
        """Crea un nuovo token di invito"""
        import secrets
        token = secrets.token_urlsafe(48)
        from datetime import timedelta
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        return cls(
            lab_code=lab_code,
            email=email,
            role=role,
            token=token,
            expires_at=expires_at,
            created_by=created_by
        )