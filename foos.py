import math
import numpy as np
import matplotlib.pyplot as pl

winningScore = 5
alpha = 0.25
C = 750.0
pMLTable = {}

def pMLLookup(score, winningScore):
	global pMLTable
	if not winningScore in pMLTable:
		# initialize the whole table for this winning score
		pMLTable[winningScore] = {}
		for n in range(winningScore):
			score1 = (n, winningScore)
			score2 = (winningScore, n)
			pMLTable[winningScore][score1] = pML(score1)
			pMLTable[winningScore][score2] = pML(score2)
	return pMLTable[winningScore][score]

def pML(score):
	# intentionally omitting 0 and 1 from the range
	p = [(n+1)/101.0 for n in range(100)]
	p.sort(key = lambda p: -1*scoreP(score, p))
	return p[0]

# final score probability!
def scoreP(score, p):
	(nA, nB) = score
	winningScore = max([nA, nB])
	memo = {}
	# nA, nB and p captured in function scope
	def f(mA, mB):
		# if this is a final score
		if mA == winningScore or mB == winningScore:
			# check whether it is valid
			return (1.0 if nA == mA and nB == mB else 0.0)

		# dynamic programming trick, memoize
		if (mA, mB) not in memo:
			memo[(mA, mB)] = p*f(mA+1, mB) + (1-p)*f(mA, mB+1)

		return memo[(mA,mB)]

	return f(0,0)

# update two ratings, RA and RB with mixing parameter alpha
def update(RA, RB, score, verbose = True, correctionFactor = 1.0):
	# the correction factor is a rating difference adjustment equal to the slope of a line correcting the bias
	# as calculated below
	dR = (RB - RA)

	# compute point spread
	pExp = 1.0/(1.0 + 10.0 ** (dR/(C * correctionFactor))) # discount dR by the correctionFactor
	if verbose:
		print("Based on the initial ratings")
		print("Team A is expected to score each point with probability " + str(pExp))
		print("Team A is expected to win with probability " + str(pWin(pExp, 5)))

	pEst = pMLLookup(score, winningScore)
	dRObs = C * math.log10((1.0/pEst) - 1)# the value of RB-RA that gives pEst
	dRObs = correctionFactor * dRObs # use the bias correction factor to adjust the estimate # use the bias correction factor to adjust the estimate

	# RA <- alpha RA + (1-alpha)RA'
	# RB <- alpha RA + (1-alpha)RB'
	# really, we're updating the estimate dREst = alpha * dR + (1-alpha) * dRObs
	dRNew = (1 - alpha) * dR + alpha * dRObs

	# and split the difference to update A and B
	RANew = round(RA + dR/2 - dRNew/2)
	RBNew = round(RB - dR/2 + dRNew/2)
	if verbose:
		print("New ratings")
		print("RA = " + str(RANew))
		print("RB = " + str(RBNew))
	return RANew, RBNew

# compute probability of first to N if probability of success per trial is p
def pWin(p,N):
	# note the following check:
	# pWin(p ,N) = sum([scoreP(N,n,p) for n in range(N)])
	# but this method is more efficient

	# use the recurrence that pWin(n = j, m = k) = p * pWin(j+1,k) + (1-p)*pWin(j,k+1)
	# very similar to score distribution calc above, but different boundary conditions
	memo = {}
	def f(j,k):
		if j == N:
			return 1.0
		if k == N:
			return 0.0

		if (j,k) not in memo:
			memo[(j,k)] = p*f(j+1, k) + (1-p)*f(j,k+1)

		return memo[(j,k)]

	return f(0,0)

# simulate two teams' rating convergence and fluctuation for 100 games:
def oneGame(p,N):
	#simulate one game, return the score
	sA = 0
	sB = 0
	rnd = np.random.rand(2*N)
	i = 0
	while (sA < N and sB < N):
		if rnd[i] < p:
			sA += 1
		else:
			sB += 1
		i += 1
	return sA, sB

def simulate(p, N, silent = False, correctionFactor = 1.0):
	rA = np.zeros(N)
	rB = np.zeros(N)

	# initial ratings
	rA[0] = 1500
	rB[0] = 1500

	# true rating
	dR = C * math.log10((1.0/p) - 1)
	rATrue = 1500 - dR/2
	rBTrue = 1500 + dR/2

	for i in range(N-1):
		rANew, rBNew = update(rA[i], rB[i], oneGame(p, winningScore), verbose = False, correctionFactor = correctionFactor)
		rA[i+1] = rANew
		rB[i+1] = rBNew
	
	if not silent:
		pl.plot(range(N), rA, 'r.-', range(N), rB, 'b.-')
		pl.legend(['Team A', 'Team B'])
		pl.axhline(rATrue, color = 'r')
		pl.axhline(rBTrue, color = 'b')
		pl.title('Rating simulation for scoring probability p = {:}\nTrue rating difference = {:.0f}'.format(p,-dR))
		pl.xlabel('Games played')
		pl.ylabel('Rating')
		pl.grid()

	return rA, rB, dR

def plotBias(n = 100, correctionFactor = 0.7):
	# n: number of p values to simulate
	# m: slope of correction line
	p = [pp/(n+1.0) for pp in range(n+1)][1:] # drop first element, since p = 0 behaves badly
	trueRating = []
	estRating = []

	for pp in p:
		ra,rb,dr = simulate(pp, 1000, True, correctionFactor)
		trueRating.append(dr)
		estRating.append(np.median(rb[500:] - ra[500:]))
	
	pl.plot(trueRating, estRating, 'r.')
	pl.plot([-1500,1500], [-1500, 1500], 'k-')
	pl.xlabel('True rating difference')
	pl.ylabel('Estimated rating difference')
	pl.title('Rating bias from simulation (correction factor = {:})'.format(correctionFactor))
	pl.grid()
