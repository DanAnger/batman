import numpy as np
import matplotlib.pyplot as plt
from . import occultnl
from . import occultquad
from . import occultuniform
from . import rsky

class TransitModel:
	"""
	
	"""
	def __init__(self, params, t, max_err, limb_dark):
		#checking for invalid input
		if (limb_dark == "uniform" and len(params.u) != 0) or (limb_dark == "linear" and len(params.u) != 1) or \
		    (limb_dark == "quadratic" and len(params.u) != 2) or (limb_dark == "nonlinear" and len(params.u) != 4):
			raise Exception("Incorrect number of coefficients for " +limb_dark + " limb darkening; u should have the form:\n \
			 u = [] for uniform LD\n \
			 u = [u1] for linear LD\n \
  			 u = [u1, u2] for quadratic LD\n \
			 u = [u1, u2, u3, u4] for nonlinear LD") 
		if limb_dark not in ["uniform", "linear", "quadratic", "nonlinear"]: 
			raise Exception("\""+limb_dark+"\""+" limb darkening not supported; allowed options are:\n \
				uniform, linear, quadratic, nonlinear")

		#initializes model parameters
		self.t = t
		self.t0 = params.t0
		self.per = params.per
		self.rp = params.rp
		self.a = params.a
		self.inc = params.inc
		self.ecc = params.ecc
		self.w = params.w 
		self.u = params.u
		self.max_err = max_err
		self.limb_dark = limb_dark
		self.zs= rsky.rsky(t, params.t0, params.per, params.a, params.inc, params.ecc, params.w)
		self.fac = self._get_fac()

#	def set_fac(self,fac):				#set scale factor manually
#		self.fac = fac

	def calc_err(self, plot = False):
		if self.limb_dark == "nonlinear":
			zs = np.linspace(0., 1.1, 500)
			fac_lo = 1.0e-4
			f0 = occultnl.occultnl(zs, self.rp, self.u[0], self.u[1], self.u[2], self.u[3], fac_lo)
			f = occultnl.occultnl(zs, self.rp, self.u[0], self.u[1], self.u[2], self.u[3], self.fac)
			err = np.max(np.abs(f-f0))*1.0e6
	#		print "Max err in light curve is " + "{0:0.2f}".format(err), "ppm"
			if plot == True:
				plt.plot(zs, 1.0e6*(f-f0), color='k')
				plt.xlabel("z (separation of centers)")
				plt.ylabel("Error (ppm)") 
				plt.show()

			return err
		else: raise Exception("Function calc_err not valid for " + self.limb_dark + " limb darkening")
	
	def _get_fac(self):
		if self.limb_dark == "nonlinear":
			fac_lo, fac_hi = 1.0e-4, 1.
			zs = np.linspace(0., 1.1, 500)
			f0 = occultnl.occultnl(zs, self.rp, self.u[0], self.u[1], self.u[2], self.u[3], fac_lo)
			n = 0
			err = 0.
			while(err > self.max_err or err < 0.99*self.max_err):
				fac = (fac_lo + fac_hi)/2.
				f = occultnl.occultnl(zs, self.rp, self.u[0], self.u[1], self.u[2], self.u[3], fac)
				err = np.max(np.abs(f-f0))*1.0e6
				if err> self.max_err: fac_hi = fac	
				else: fac_lo = fac
				n += 1
				if n>1e4: raise Exception("Convergence failure in calculation of scale factor for occultnl")
			return fac
		else: return 0.

	def LightCurve(self, params):
		if self.limb_dark == "quadratic": return occultquad.occultquad(self.zs, params.rp, params.u[0], params.u[1])
		elif self.limb_dark == "nonlinear": return occultnl.occultnl(self.zs, params.rp, params.u[0], params.u[1], params.u[2], params.u[3], self.fac)
		elif self.limb_dark == "linear": return occultquad.occultquad(self.zs, params.rp, params.u[0], 0.)
		elif self.limb_dark == "uniform": return occultuniform.occultuniform(self.zs, params.rp)
			

class TransitParams(object):
	"""
	doc
	"""
	def __init__(self):
		self.t0 = 0.
		self.per = 0.
		self.rp = 0.
		self.a = 0.
		self.inc = 0.
		self.ecc = 0.
		self.w = 0. 
		self.u = []
