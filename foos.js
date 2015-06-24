// global parameters controlling system behavior
var alpha = 0.125 // controls sensitivity/aggression of the updates
var C = 750.0 // controls the spread in values
var correctionFactor = 0.7 // discount the point spread to eliminate bias
var winningScore = 5 // game to 5

$(document).ready(function(){
	$('#details').hide()
	$('#update-button').attr("onClick", "handle(this.form)")
	$('#rating-form').change(function(e){
		// check if both ratingA and ratingB are filled in
		var form = $('#rating-form').serializeArray()
		var rA = form.filter(function(o){return o.name == "ratingA"})[0].value
		var rB = form.filter(function(o){return o.name == "ratingB"})[0].value
		var sc = form.filter(function(o){return o.name == "score"})[0].value
		if (sc != "") { // if a score has been entered, then update
			$('#update-button').click()
		} else if (rA != "" && rB != "") {
			$('#result').html('<div class="output">> ' + handicap(rA, rB).messageArray.join("<br>> ") + '</div>')
		} else {
		}
	})
})

function handle(form){
	var RA = parseInt(form.ratingA.value)
	var RB = parseInt(form.ratingB.value)
	var sc = form.score.value.split("-") // e.g. ["5","4"]
	var nA = parseInt(sc[0])
	var nB = parseInt(sc[1])
	var result = '> ' + update(RA,RB,nA,nB).join("<br>> ")
	$('#result').html('<div class="output">' + result + '</div>')
}

function handicap(RA, RB) {
	var dR = RB - RA
	// expected goal scoring probability of team A, based on the rating difference
	// this is the probability that A scores any particular goal, which is *not*
	// the probability that A wins
	var pExpected = 1.0 / (1.0 + Math.pow(10.0, dR / (C * correctionFactor)))

	return {
		'pExpected': pExpected,
		'messageArray':
			[("Team A (" + RA + ") is expected to score with probability " + pExpected.toFixed(2)),
			("Team B (" + RB + ") is expected to score with probability " + (1.0 - pExpected).toFixed(2)),
			("Team A is expected to win with probability " + pWin(pExpected, winningScore).toFixed(2)),
			("The score differential is expected to be " + spread(pExpected, winningScore).toFixed(2))]
		}

}

function update(RA, RB, nA, nB) {
	var dR = RB - RA
	// maximum likelihood value of p given the score
	var pEstimated = pML(nA, nB)
	// compute the value of dR that would yield the ML estimate above
	// this step is why 0 and 1 are excluded from candidate values of pML below
	var dREstimated = correctionFactor * C * Math.log((1.0/pEstimated) - 1)/Math.log(10) // hmm safari didn't like Math.log10()
	var dRNew = (1 - alpha) * dR + alpha * dREstimated

	RANew = Math.round(RA + (dR - dRNew)/2)
	RBNew = Math.round(RB - (dR - dRNew)/2)

	return [("Based on the actual score of " + nA + "-" + nB),
	("Ratings are updated to"),
	("<font color='#4cae4c'>Rating A = " + RANew + "</font>"),
	("<font color='#4cae4c'>Rating B = " + RBNew + "</font>")]
}

// likelihood function p(score | p) for the final score nA, nB
// assumes nA,nB is a final score and the game was played until one
// team reached max(nA, nB) -- no "win by 2" rules or anything
function likelihood(nA, nB, p) {
	var winningScore = Math.max(nA, nB)
	var memo = {}

	function f(mA, mB) {
		if ((mA == winningScore) || (mB == winningScore)) {
			if ((nA == mA) && (nB == mB)) return 1.0
			else return 0.0
		}

		var key = mA + "," + mB

		if (Object.keys(memo).indexOf(key) == -1)
			memo[key] = p * f(mA + 1, mB) + (1 - p) * f(mA, mB + 1)

		return memo[key]
	}

	return f(0,0)
}

function spread(p, winningScore) {
	var d = 0
	for(nA = 0; nA < (winningScore +1); nA++){ d += likelihood(nA, winningScore, p)*(nA - winningScore) }
	for(nB = 0; nB < (winningScore +1); nB++){ d += likelihood(winningScore, nB, p)*(winningScore - nB) }

	return d
}

// maximum likelihood computed by simple 1D grid search
function pML(nA, nB) {
	// intentionally do not allow the values 0 or 1 in the range, as they will mess up the
	// score update function (0 and 1 correspond to infinite rating differentials)
	var N = 100
	var p = new Array(N-1)
	for(i = 1; i < N; i ++) {
		p[i-1] = i/N
	}

	p.sort(function(p1,p2){
		return likelihood(nA, nB, p2) - likelihood(nA, nB, p1)
	})

	return p[0]
}

// overall win probability
// similar calc to score distribution, but with different base cases
function pWin(p, winningScore) {
	var memo = {}

	var f = function(mA, mB) {
		if (mA == winningScore) return 1.0
		if (mB == winningScore) return 0.0

		var key = mA + "," + mB

		if (Object.keys(memo).indexOf(key) == -1)
			memo[key] = p * f(mA + 1, mB) + (1 - p) * f(mA, mB + 1)

		return memo[key]
	}

	return f(0,0)
}
