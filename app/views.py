import base64, csv, StringIO

from flask import render_template, flash, redirect, session, url_for, request, g, send_file
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message

from app import app, db, mail, team_icons
from app.forms import *
from app.models import *

def send_email(subject, recipients, email_template, **kwargs):
    body = render_template(email_template, **kwargs)
    if app.config.get('EMAIL_DEBUG'):
        print('Subject: %s' % subject)
        print('To: %s' % ', '.join(recipients))
        print('Body: %s' % body)
        return

    msg = Message(subject, sender="bonzai-support-l@mtu.edu", recipients=recipients)
    msg.body = body
    mail.send(msg)

@app.errorhandler(404)
def page_not_found(e):
        return render_template('404.html'), 404

@app.before_request
def before_request():
    # Store the current user in a flask global
    g.user = current_user

@app.route('/')
@app.route('/index')
@login_required
def index():
    # The index is a dashboard with the current user's team,
    # registration status and similar other info.
    return render_template('show_user.html', user=g.user)

@app.route('/users/<int:user_id>')
@login_required
def show_user(user_id):
    if not g.user.is_admin:
        flash('You do not have permission to view that')
        return redirect(url_for('index'))

    return render_template('show_user.html',
                           user=User.query.get_or_404(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated():
        flash('You are already logged in!')
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        if not form.user.is_active():
            flash('Please confirm your email before logging in.')
        else:
            login_user(form.user)
            return redirect(request.args.get('next') or url_for('index'))

    return render_template('form.html',
                           form=form,
                           action='Login',
                           action_url=url_for('login', next=request.args.get('next')),
                           title='Login')

@app.route('/logout')
def logout():
    if g.user.is_authenticated():
        flash('You have been logged out.')

    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user.is_authenticated():
        flash('You are already logged in!')
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = form.save()
        if user:
            flash('You have been registered. Please confirm your email.')
            send_email("[BonzaiBrawl] Please confirm your email", [user.email],
                       "user_register.txt", user=user,
                       next=request.args.get('next'))
            return redirect(url_for('login'))
        else:
            flash('A user with that email already exists', 'danger')
            form.email.data = ''

    if form.errors:
        flash('An error occured', 'danger')

    return render_template('registration.html',
                           form=form,
                           action='Register',
                           action_url=url_for('register', next=request.args.get('next')))

@app.route('/confirm/<uuid>')
def confirm_email(uuid):
    if g.user.is_authenticated():
        flash('You are already logged in!')
        return redirect(url_for('index'))

    user = User.query.filter_by(confirmation=uuid).first_or_404()
    user.confirmation = None
    db.session.merge(user)
    db.session.commit()

    login_user(user)
    flash('Your email has been confirmed and you have been logged in.')
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/users')
@login_required
def list_users():
    # List users is mostly an admin view
    if not g.user.is_admin:
        flash("You don't have permission to view that.")
        return redirect(url_for('index'))

    users = User.query.order_by(User.name).all()
    return render_template('list_users.html', users=users)

@app.route('/teams')
@login_required
def list_teams():
    # List teams is mostly an admin view
    if not g.user.is_admin:
        flash("You don't have permission to view that.")
        return redirect(url_for('index'))

    teams = Team.query.order_by(Team.name).all()
    return render_template('list_teams.html', teams=teams)

@app.route('/teams/new', methods=['GET', 'POST'])
@login_required
def create_team():
    if g.user.team is not None:
        flash("You are already a part of a team!")
        return redirect(url_for('index'))

    team = Team()
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        form.populate_obj(team)
        db.session.add(team)
        db.session.commit()

        # Store the filename we have for them
        team.icon_name = team_icons.save(form.icon.data, name='%d.' % team.id)
        db.session.merge(team)

        # Update the current user to be in this team
        g.user.team_id = team.id
        db.session.merge(g.user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('create_team.html', form=form, title='Create Team')

@app.route('/teams/<int:team_id>/toggle_paid', methods=['GET', 'POST'])
def toggle_team_paid(team_id):
    if not g.user.is_admin:
        flash("You do not have permission to do that!")
        return redirect(url_for('index'))

    # Toggle the team's paid status
    team = Team.query.get_or_404(team_id)
    team.paid = not team.paid

    # Commit the changes to the db
    db.session.merge(team)
    db.session.commit()

    return redirect(url_for('list_teams'))

@app.route('/teams/<int:team_id>/edit', methods=['GET', 'POST'])
def edit_team(team_id):
    if not g.user.is_admin and g.user.team is None:
        flash("You are not a part of a team yet!")
        return redirect(url_for('index'))

    if not g.user.is_admin and g.user.team_id != team_id:
        flash("You don't have permission to edit that.")
        return redirect(url_for('index'))

    # Look up the team and create the form we need
    team = Team.query.get_or_404(team_id)
    form = EditTeamForm(obj=team)

    if form.validate_on_submit():
        form.populate_obj(team)
        db.session.merge(team)
        db.session.commit()

        # Only update the icon if we need to
        if form.icon.data:
            # Store the filename we have for them
            team.icon_name = team_icons.save(form.icon.data, name='%d.' % team.id)
            db.session.merge(team)
            db.session.commit()

        return redirect(url_for('index'))

    return render_template('form.html', form=form)

#shows current members & user can pick & leave
@app.route('/join/<team_lookup>')
@login_required
def confirm_join_team(team_lookup):
    if g.user.team_id is not None:
        flash("You are already a part of a team!")
        return redirect(url_for('index'))

    team = Team.query.filter_by(secret=team_lookup).first_or_404()

    return render_template('join_team.html', team=team)

#actually adds user to team, link on confirm join team
@app.route('/join/<team_lookup>/confirm')
@login_required
def join_team(team_lookup):
    if g.user.team_id is not None:
        flash("You are already a part of a team!")
        return redirect(url_for('index'))

    team = Team.query.filter_by(secret=team_lookup).first_or_404()

    if team.is_full:
        flash("This team is already full.")
        return redirect(url_for('confirm_join_team', team_lookup=team_lookup))

    send_email(
        "[BonzaiBrawl] A user has joined your team",
        [u.email for u in team.members],
        "team_join.txt",
        user=g.user
    )

    # Set our current team to the team we found
    g.user.team_id = team.id

    # Stage our user to be comitted
    db.session.merge(g.user)

    # Save the change
    db.session.commit()

    flash("You have joined team %s" % team.name)

    return redirect(url_for('index'))

@app.route('/join/<team_lookup>/leave')
def leave_team(team_lookup):
    if g.user.team is None:
        flash("You are not a part of a team yet!")
        return redirect(url_for('index'))

    team = Team.query.filter_by(secret=team_lookup).first_or_404()

    # They're only allowed to leave a team they're in
    if g.user.team_id is not team.id:
        flash("You are not a part of this team!")
        return redirect(url_for('index'))

    # Set our current team to nothing
    g.user.team_id = None

    # Stage our user to be comitted
    db.session.merge(g.user)

    # If we are the only current team member, delete the team
    if len(team.members) == 0:
        db.session.delete(team)

    # Save the change
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if not g.user.is_admin:
        if g.user.id != user_id:
            flash("You do not have permission to do that!")
            return redirect(url_for('index'))

        # Allow the user to change display name, etc
        if user.team is not None and user.team.is_paid:
            flash("You cannot change your profile. Your team has paid.")
            return redirect(url_for('index'))

    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.merge(user)
        db.session.commit()

        flash("You have updated your profile.")
        return redirect(url_for('show_user', user_id=user.id))

    return render_template('edit_user.html',
                            form=form,
                            title='Edit User')

@app.route('/users/csv')
@login_required
def csv_users():
    # List users is mostly an admin view
    if not g.user.is_admin:
        flash("You don't have permission to view that.")
        return redirect(url_for('index'))
    # Create string as file
    csvfile = StringIO.StringIO()
    # Create CSV writer
    writer = csv.writer(csvfile, dialect='excel')
    result = User.query.order_by(User.name).all()
    # Query Users and Write to CSV
    for row in result:
        #print row
        if row.team:
            writer.writerow([row.email, row.team.name, row.team_id, row.name, row.shirt_size, row.team.location,  row.team.paid, row.food_preferences, row.food_other])
        else:
            writer.writerow([row.email, "None", "N/A", row.name, row.shirt_size, "N/A", "False", row.food_preferences, row.food_other])
    csvfile.seek(0)
    # Return CSV for download
    return send_file(csvfile, as_attachment='True', attachment_filename='users.csv')
