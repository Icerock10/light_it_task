from django.shortcuts import render, redirect
from .models import Tournament, Stage, Player, Team, Round, Match
from .forms import NewTournament, NewStage
from django.views.decorators.http import require_POST
import random


def main(request):
    tournaments = Tournament.objects.all()
    context = {
        'tournaments': tournaments,
    }
    is_tourn_admin = request.user.groups.filter(name='tournament_admin').exists()
    if is_tourn_admin:
        tournament_form = NewTournament()
        stage_form = NewStage()
        context['new_tourn_form'] = tournament_form
        context['is_tourn_admin'] = is_tourn_admin
        context['new_stage_form'] = stage_form
    return render(request, 'tournament/main.html', context)


@require_POST
def create_tournament(request):
    tournament_form = NewTournament(request.POST)
    if tournament_form.is_valid():
        tournament_form = tournament_form.save()
        stage_form = NewStage(request.POST)
        new_tournament_id = stage_form.save(commit=False)
        new_tournament_id.tournament_id = tournament_form.id
        new_tournament_id.save()
        stage = stage_form.save()
        round = Round(stage_id=stage.id)
        round.save()
    return redirect('main')


def delete_tournament(request, tournament_id):
    Tournament.objects.filter(id=tournament_id).delete()
    return redirect('main')


def create_teams(request, tournament_id):
    if Team.objects.filter(tournament_id=tournament_id).exists():
        return redirect('main')
    tournament = Tournament.objects.get(id=tournament_id)
    players = tournament.players.all().order_by('rank')
    half = int(len(players)/2)
    weak, strong = (players[:half], players[half:])
    while weak:
        if random.random() > 0.8:
            p1 = weak.pop(random.randrange(len(weak)))  # need to rid of len
            p2 = strong.pop(random.randrange(len(strong)))
        else:
            p1 = weak.pop(0)
            p2 = strong.pop()
        team_name = '{p1_l} {p1_f}. | {p2_l} {p2_f}.'.format(
            p1_f=p1.first_name[0],
            p1_l=p1.last_name,
            p2_f=p2.first_name[0],
            p2_l=p2.last_name,)
        team = Team(name=team_name, tournament=tournament)
        team.save()  # maybe there is better way without using save() two times
        team.players.add(p1, p2)
        team.save()
    return redirect('main')


def tournament(request, tournament_name):
    get_tournament = Tournament.objects.get(name=tournament_name)
    get_stages = get_tournament.stage_set.all()
    context = {
        'tournament': get_tournament,
        'tournament_name': tournament_name,
        'stages': get_stages
    }
    return render(request, 'tournament/tournament.html', context)


def table(request, tournament_name, stage_id):
    get_stage = Stage.objects.get(id=stage_id)
    tournament_id = get_stage.tournament_id
    teams = Team.objects.filter(tournament_id=tournament_id)
    context = {
        'stage': get_stage,
        't_name': tournament_name,
        'teams': teams
    }
    if get_stage.mode == "PO":
        return render(request, 'tournament/table_po.html', context)
    else:
        return render(request, 'tournament/table_reg.html', context)


def edit_profile(request):
    if request.user.is_anonymous:
        return redirect('main')
    player = Player.objects.get(user=request.user)
    full_name = '%s %s' % (player.first_name, player.last_name)
    context = {'player': player, 'full_name': full_name}
    social_acc = request.user.socialaccount_set.all().first()
    if social_acc:
        social_ava = social_acc.get_avatar_url()
        context['social_ava'] = social_ava
    return render(request, 'tournament/player_profile.html', context)


def about(request):
    return render(request, 'tournament/about.html')


def players(request):
    get_players = Player.objects.all()
    context = {'players': get_players}
    return render(request, 'tournament/players.html', context)


def create_matches(request, tournament_name, stage_id):
    get_stage = Stage.objects.get(id=stage_id)
    tournament_id = get_stage.tournament_id
    teams = Team.objects.filter(tournament_id=tournament_id)
    rounds = Round.objects.filter(stage_id=stage_id)
    if not Match.objects.filter(round_id=rounds[0].id).exists():
        matches = match_generator(list(teams))
        for team in matches:
            obj_match = Match(round=rounds[0],
                              team_1_score='%d:0' % team[0].id,
                              team_2_score='%d:0' % team[1].id,
                              )
            obj_match.save()
            obj_match.teams.add(team[0], team[1])
    return redirect('tournament', tournament_name)


def show_matches(request, tournament_name, stage_id):
    rounds = Round.objects.filter(stage_id=stage_id)
    matches_list = Match.objects.filter(round_id=rounds[0].id)
    render_matches = []
    for match in matches_list:
        teams_and_match = [match.teams.all(), match]
        render_matches.append(teams_and_match)
    context = {
        'render_matches': render_matches,
        'tournament_name': tournament_name,
        'stage_id': stage_id,
    }
    return render(request, 'tournament/matches.html', context)


def match_generator(teams):
    match = []
    while teams:
        team1 = teams.pop()
        for team2 in teams:
            match.append([team1, team2])
    return match
