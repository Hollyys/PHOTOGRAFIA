from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photografia_members.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 고유 id
    name = db.Column(db.String(100), nullable=False) # 이름
    gender = db.Column(db.String(10), nullable=False) # 성별
    residence = db.Column(db.String(100), nullable=False) # 거주지
    birth_date = db.Column(db.Date, nullable=False) # 생년월일
    join_date = db.Column(db.Date, default=datetime.utcnow, nullable=False) # 모임 가입일
    one_month_status = db.Column(db.String(1), default='X', nullable=False)  # 가입 한 달 여부 O/X
    notice_participation = db.Column(db.String(1), default='X', nullable=False)  # 공지방 참여 여부 O/X
    warnings = db.Column(db.Integer, default=0, nullable=False) # 경고 횟수
    notes = db.Column(db.String(200), default='', nullable=True) # 비고

    def to_dict(self):
        return {
            'id': self.id,
            '이름': self.name,
            '성별': self.gender,
            '거주지': self.residence,
            '생년월일': self.birth_date.strftime('%Y-%m-%d'),
            '모임 가입일': self.join_date.strftime('%Y-%m-%d'),
            '가입 한 달 여부': self.one_month_status,
            '공지방 참여': self.notice_participation,
            '경고횟수': self.warnings,
            '비고란': self.notes
        }

@app.route('/members', methods=['POST'])
def add_member():
    data = request.json
    try:
        new_member = Member(
            name=data['이름'],
            gender=data['성별'],
            residence=data['거주지'],
            birth_date=datetime.strptime(data['생년월일'], '%Y-%m-%d'),
            join_date=datetime.strptime(data['모임 가입일'], '%Y-%m-%d') if 'join_date' in data else datetime.utcnow(),
            notice_participation=data.get('공지방 참여', 'X'),
            warnings=data.get('경고횟수', 0),
            notes=data.get('비고란', '')
        )

        if new_member.join_date + timedelta(days=30) <= datetime.utcnow():
            new_member.one_month_status = 'O'

        db.session.add(new_member)
        db.session.commit()

        return jsonify({'message': 'Member added successfully!', 'member': new_member.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([member.to_dict() for member in members])

@app.route('/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    member = Member.query.get_or_404(member_id)
    return jsonify(member.to_dict())

@app.route('/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.json
    member = Member.query.get_or_404(member_id)

    try:
        member.name = data.get('name', member.name)
        member.gender = data.get('gender', member.gender)
        member.residence = data.get('residence', member.residence)
        if 'birth_date' in data:
            member.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d')
        if 'join_date' in data:
            member.join_date = datetime.strptime(data['join_date'], '%Y-%m-%d')
        member.notice_participation = data.get('notice_participation', member.notice_participation)
        member.warnings = data.get('warnings', member.warnings)
        member.notes = data.get('notes', member.notes)

        if member.join_date + timedelta(days=30) <= datetime.utcnow():
            member.one_month_status = 'O'
        else:
            member.one_month_status = 'X'

        db.session.commit()

        return jsonify({'message': 'Member updated successfully!', 'member': member.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully!'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()    

    app.run(host="0.0.0.0", debug=True)
