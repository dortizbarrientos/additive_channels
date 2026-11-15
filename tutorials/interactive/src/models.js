/* The numerical rules used by the teaching controls.
   G is a variance (or covariance matrix), H is curvature, and b is a slope.
   These functions contain no interface code, so their results can be checked
   independently against the Python calculations in the source repository. */
(function (root) {
  'use strict';
  const finite = x => Number.isFinite(x);
  const sum = xs => xs.reduce((a,b) => a+b,0);
  const mean = xs => sum(xs)/xs.length;
  function components(b,H,G) {
    if(![b,H,G].every(finite)||G<0) throw new Error('Use a finite, nonnegative variance.');
    const linear=b*b*G, curved=0.5*H*H*G*G, total=linear+curved;
    return {linear,curved,total,share:total>0?linear/total:null,intercept:0.5*H*G};
  }
  // For ell(x)=b*x+H*x^2/2-kappa*x^4 under a centred Gaussian.
  // The odd linear term is uncorrelated with the complete even remainder.
  function quarticComponents(b,H,G,kappa) {
    if(!finite(kappa)||kappa<0) throw new Error('Use a finite, nonnegative quartic coefficient.');
    const local=components(b,H,G);
    const evenVariance=.5*H*H*G*G-12*H*kappa*G**3+96*kappa*kappa*G**4;
    const total=local.linear+evenVariance;
    return {linear:local.linear,localShare:local.share,evenVariance,total,
      fullShare:total>0?local.linear/total:null,fittedInterceptShift:.5*H*G-3*kappa*G*G};
  }
  function normal(x,mu,variance) {
    return variance>0?Math.exp(-((x-mu)**2)/(2*variance))/Math.sqrt(2*Math.PI*variance):0;
  }
  function selection(b,H,G) {
    const denominator=1-H*G, linear=G*b;
    if(denominator<=0) return {normalisable:false,denominator,linear,exact:null,variance:null,relativeError:null};
    const exact=linear/denominator;
    return {normalisable:true,denominator,linear,exact,variance:G/denominator,
      relativeError:exact!==0?Math.abs(linear-exact)/Math.abs(exact):null,
      signedRelativeError:exact!==0?(linear-exact)/exact:null,scaledCurvature:Math.abs(H*G)};
  }
  function rotateCovariance(degrees,longVariance=.20,shortVariance=.005) {
    const angle=degrees*Math.PI/180,c=Math.cos(angle),s=Math.sin(angle);
    return [[longVariance*c*c+shortVariance*s*s,(longVariance-shortVariance)*c*s],
      [(longVariance-shortVariance)*c*s,longVariance*s*s+shortVariance*c*c]];
  }
  function geometry(degrees) {
    const G=rotateCovariance(degrees),linear=.6525*G[0][0],curved=.32*(.20**2+.005**2);
    return {G,linear,curved,share:linear/(linear+curved),b:Math.sqrt(.6525),H:-.8};
  }
  function inheritanceStep(g,B,gamma,rho) {
    return (1-rho)*B+rho*g/(1+gamma*g);
  }
  function fixedPoint(B,gamma,rho) {
    if(!(B>0&&gamma>=0&&rho>=0&&rho<1)) throw new Error('Use B>0, gamma>=0 and 0<=rho<1.');
    if(gamma===0) return B;
    const A=(1-rho)*B,coefficient=1-rho-A*gamma;
    const discriminant=Math.sqrt(coefficient*coefficient+4*gamma*A);
    // Choose the equivalent root that avoids subtracting nearly equal values.
    return coefficient>=0?2*A/(coefficient+discriminant):(-coefficient+discriminant)/(2*gamma);
  }
  function inheritance(p,generations=80) {
    let g=p.g0; const path=[];
    for(let t=0;t<=generations;t++) {
      const declining=p.b*Math.exp(-.06*Math.max(0,t-40));
      const curved=.5*p.n*p.gamma*p.gamma*g*g;
      const linear=p.b*p.b*g, decliningLinear=declining*declining*g;
      path.push({t,g,selected:g/(1+p.gamma*g),linear,curved,
        share:linear+curved>0?linear/(linear+curved):null,
        decliningGradient:declining,
        decliningShare:decliningLinear+curved>0?decliningLinear/(decliningLinear+curved):null});
      g=inheritanceStep(g,p.B,p.gamma,p.rho);
    }
    return {path,fixedPoint:fixedPoint(p.B,p.gamma,p.rho)};
  }
  function quantile(values,p) {
    const a=values.slice().sort((x,y)=>x-y),position=(a.length-1)*p,lo=Math.floor(position),f=position-lo;
    return a[lo]+f*((a[lo+1]??a[lo])-a[lo]);
  }
  function histogram(values,lo,hi,bins) {
    const counts=Array(bins).fill(0),width=(hi-lo)/bins;
    for(const x of values) if(x>=lo&&x<=hi)counts[Math.min(bins-1,Math.floor((x-lo)/width))]++;
    return counts.map((count,i)=>({x:lo+(i+.5)*width,left:lo+i*width,right:lo+(i+1)*width,count}));
  }
  // The measurement model gives a normal distribution for a centred breeding
  // value, conditional on this genotype's repeated height measurements.
  function posterior(heights,calibration) {
    const average=mean(heights),r=heights.length;
    const reliability=calibration.G/(calibration.G+calibration.E/r);
    return {average,reliability,mean:reliability*(average-calibration.mu),variance:calibration.G*(1-reliability)};
  }
  function expectedCount(m,v,theta) {
    const [alpha,b,H]=theta,d=1-H*v;
    if(d<=0)return null;
    return Math.exp(alpha+b*m+.5*H*m*m+v*(b+H*m)**2/(2*d))/Math.sqrt(d);
  }
  // Numerical integration is only used to demonstrate an individual's count
  // probability. It never refits or changes the saved reference estimates.
  function countProbability(count,m,v,theta,quadrature) {
    let logFactorial=0;for(let i=2;i<=count;i++)logFactorial+=Math.log(i);
    const [alpha,b,H]=theta;
    return sum(quadrature.nodes.map((u,i)=>{
      const z=m+Math.sqrt(v)*u,eta=alpha+b*z+.5*H*z*z;
      return quadrature.weights[i]*Math.exp(count*eta-Math.exp(eta)-logFactorial);
    }));
  }
  function nonGaussianExample() {
    const x=[-1,2],p=[2/3,1/3],L=x,Q=x.map(z=>.5*z*z),y=x.map((z,i)=>L[i]+Q[i]);
    const weightedMean=a=>sum(a.map((z,i)=>p[i]*z));
    const variance=a=>{const m=weightedMean(a);return sum(a.map((z,i)=>p[i]*(z-m)**2));};
    const cov=(a,b)=>{const ma=weightedMean(a),mb=weightedMean(b);return sum(a.map((z,i)=>p[i]*(z-ma)*(b[i]-mb)));};
    return {G:variance(x),linear:variance(L),curved:variance(Q),covariance:cov(L,Q),total:variance(y),
      slope:cov(x,y)/variance(x),intercept:weightedMean(y),R2:cov(x,y)**2/(variance(x)*variance(y)),gaussianFormula:components(1,1,variance(x)).share};
  }
  root.ChannelMath={sum,mean,components,quarticComponents,normal,selection,rotateCovariance,geometry,inheritanceStep,fixedPoint,inheritance,quantile,histogram,posterior,expectedCount,countProbability,nonGaussianExample};
  if(typeof module!=='undefined'&&module.exports)module.exports=root.ChannelMath;
})(typeof globalThis!=='undefined'?globalThis:this);
