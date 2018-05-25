'''data structures for encoding matpower data files'''

# import bus, branch, area, generator
import copy
import warnings

from grg_mpdata.exception import MPDataValidationError
from grg_mpdata.exception import MPDataWarning


def _guard_none(fun, val):
    '''guards the application of a unary function for values taking None
    useful for typing optional values

    Args:
        fun: a function
        val: a unary value
    Returns:
        None if val was None, otherwise the application of fun to val
    '''

    if val is None:
        return None
    else:
        return fun(val)


class Case(object):
    def __init__(self, name=None, version=None, baseMVA=None, bus=None,
                 gen=None, branch=None, gencost=None, dcline=None, dclinecost=None, busname=None):
        '''This data structure contains lists of all the key components in a
        power network.  All arguments have default values to allow clear error
        messages to be generated in the validation method.  At this time, only
        Matpower case version 2 is supported.

        Args:
            name (str): textual name of the test case.  Must be a valid matlab
                function identifier
            version (str): indicates the version of the test case
            baseMVA (float): the network MVA base value (MVA)
            bus (list of Bus): network buses
            gen (list of Generator): network generators
            branch (list of Branch): network branches
            gencost (list of GeneratorCost, optional): generator cost models
            dcline (list of DCLine, optional): network DC lines
            dclinecost (list of DCLineCost, optional): DC line cost models
            busname (list of BusName, optional): string names of items in bus list
        '''

        self.name = name
        self.version = version
        self.baseMVA = _guard_none(float, baseMVA)
        self.bus = bus
        self.gen = gen
        self.branch = branch
        self.gencost = gencost
        self.dcline = dcline
        self.dclinecost = dclinecost
        self.busname = busname

    def __str__(self):
        tmp = []
        tmp += ['Base:\n']
        tmp += [self.name+' '+str(self.version)+' '+str(self.baseMVA)+'\n']
        tmp += ['\n']

        tmp += ['Buses:\n']
        tmp += ['\n'.join([str(x) for x in self.bus])]
        tmp += ['\n \n']

        tmp += ['Generators:\n']
        tmp += ['\n'.join([str(x) for x in self.gen])]
        tmp += ['\n \n']

        tmp += ['Generator Costs:\n']
        if self.gencost is not None:
            tmp += ['\n'.join([str(x) for x in self.gencost])]
        else:
            tmp += ['None']
        tmp += ['\n \n']

        tmp += ['Branches:\n']
        tmp += ['\n'.join([str(x) for x in self.branch])]
        tmp += ['\n \n']

        tmp += ['DC Lines:\n']
        if self.dcline is not None:
            tmp += ['\n'.join([str(x) for x in self.dcline])]
        else:
            tmp += ['None']
        tmp += ['\n \n']

        tmp += ['DC Lines Costs:\n']
        if self.dclinecost is not None:
            tmp += ['\n'.join([str(x) for x in self.dclinecost])]
        else:
            tmp += ['None']
        tmp += ['\n \n']

        tmp += ['Bus Names:\n']
        if self.busname is not None:
            tmp += ['\n'.join([str(x) for x in self.busname])]
        else:
            tmp += ['None']
        tmp += ['\n']

        return ''.join(tmp)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            # if not self.__dict__ == other.__dict__:
            #     for k in self.__dict__.keys():
            #        if not k in other.__dict__:
            #            print 'No key', k
            #        else:
            #            print k, self.__dict__[k] == other.__dict__[k]
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def validate(self):
        '''Checks that this data structure conforms to the Matpower data
        specification.
        '''

        # NOTE: this function only check conformance to the official data spec.
        # Other levels of correctness are out of scope.

        if self.version is None:
            raise MPDataValidationError('case has no version')
        if self.name is None:
            raise MPDataValidationError('case has no name')
        if self.baseMVA is None:
            raise MPDataValidationError('case has no baseMVA value')
        if self.bus is None:
            raise MPDataValidationError('case has no buses')
        if self.gen is None:
            raise MPDataValidationError('case has no generators')
        if self.branch is None:
            raise MPDataValidationError('case has no branches')

        if self.version != '\'2\'':
            warnings.warn('this data structure was designed for only version '
                '\'2\'. Given %s' % self.version, MPDataWarning)

        for bus in self.bus:
            bus.validate()

        if self.busname is not None:
            if len(self.bus) != len(self.busname):
                raise MPDataValidationError('number of given bus names does '
                    'not match the number of buses')

        if self.gencost is not None:
            if not (len(self.gencost) == len(self.gen) or
                    len(self.gencost) == 2*len(self.gen)):
                raise MPDataValidationError('number of gencost items does not '
                    'match the number of generators')
            for gencost in self.gencost:
                gencost.validate()

            if len(self.gencost) > len(self.gen):
                # we can assume there are 2x gen costs
                offset = len(self.gen)
                for i in range(0, len(self.gen)):
                    active_cost = self.gencost[i]
                    reactive_cost = self.gencost[i+offset]
                    if active_cost.startup != reactive_cost.startup:
                        raise MPDataValidationError('startup values on active '
                            'and reactive power cost functions on generator '
                            '%d are not consistent' % self.gen[i].index)

                    if active_cost.shutdown != reactive_cost.shutdown:
                        raise MPDataValidationError('shutdown values on '
                            'active and reactive power cost functions on '
                            'generator %d are not consistent' 
                            % self.gen[i].index)

        if self.dclinecost is not None:
            if not (len(self.dclinecost) == len(self.dclinecost)):
                raise MPDataValidationError('number of dclinecost items does not '
                    'match the number of dclines')
            for dclinecost in self.dclinecost:
                dclinecost.validate()

        for branch in self.branch:
            branch.validate()

        if self.dcline is not None:
            for dcline in self.dcline:
                dcline.validate()

    def to_matpower(self):
        '''Returns: a Matpower encoding of this data structure as a string'''

        matpower_lines = []
        matpower_lines.append('function mpc = '+str(self.name))
        matpower_lines.append('mpc.version = '+str(self.version)+';')
        matpower_lines.append('mpc.baseMVA = '+str(self.baseMVA)+';')

        matpower_lines.append('')
        matpower_lines.append('%% bus data')
        header_names = ['bus_i', 'bus_type', 'pd', 'qd', 'gs', 'bs',
                        'bus_area', 'vm', 'va', 'base_kv', 'zone', 'vmax',
                        'vmin']
        if any([bus.extended for bus in self.bus]):
            header_names += ['lam_p', 'lam_q', 'mu_vmax', 'mu_vmin']
        matpower_lines.append('%\t'+'\t'.join(header_names))
        matpower_lines.append('mpc.bus = [')
        for bus in self.bus:
            matpower_lines.append('\t'+bus.to_matpower()+';')
        matpower_lines.append('];')

        matpower_lines.append('')
        matpower_lines.append('%% generator data')
        header_names = ['gen_bus', 'pg', 'qg', 'qmax', 'qmin', 'vg', 'mbase',
                        'gen_status', 'pmax', 'pmin', 'pc1', 'pc2', 'qc1min',
                        'qc1max', 'qc2min', 'qc2max', 'ramp_agc', 'ramp_10',
                        'ramp_30', 'ramp_q', 'apf']
        if any([gen.extended for gen in self.gen]):
            header_names += ['mu_pmax', 'mu_pmin', 'mu_qmax', 'mu_qmin']
        matpower_lines.append('%\t'+'\t'.join(header_names))
        matpower_lines.append('mpc.gen = [')
        for gen in self.gen:
            matpower_lines.append('\t'+gen.to_matpower()+';')
        matpower_lines.append('];')

        if self.gencost is not None:
            matpower_lines.append('')
            matpower_lines.append('%% generator cost data')
            header_names = ['1', 'startup', 'shutdown', 'ncost', ' x_1',
                            'y_1', '...', 'x_ncost', 'y_ncost']
            matpower_lines.append('%\t'+'\t'.join(header_names))
            header_names = ['2', 'startup', 'shutdown', 'ncost',
                            ' c_(ncost-1)', '...', 'c_0']
            matpower_lines.append('%\t'+'\t'.join(header_names))
            matpower_lines.append('mpc.gencost = [')
            for gencost in self.gencost:
                matpower_lines.append('\t'+gencost.to_matpower()+';')
            matpower_lines.append('];')

        matpower_lines.append('')
        matpower_lines.append('%% branch data')
        header_names = ['f_bus', 't_bus', 'br_r', 'br_x', 'br_b', 'rate_a',
                        'rate_b', 'rate_c', 'tap', 'shift', 'br_status',
                        'angmin', 'angmax']
        if any([gen.extended for gen in self.gen]):
            header_names += ['pf', 'qf', 'pt', 'qt', 'mu_sf', 'mu_st',
                             'mu_angmin', 'mu_angmax']
        matpower_lines.append('%\t'+'\t'.join(header_names))
        matpower_lines.append('mpc.branch = [')
        for branch in self.branch:
            matpower_lines.append('\t'+branch.to_matpower()+';')
        matpower_lines.append('];')

        if self.dcline is not None:
            matpower_lines.append('')
            matpower_lines.append('%% dc line data')
            header_names = ['f_bus', 't_bus', 'br_r', 'br_x', 'br_b', 'rate_a',
                            'rate_b', 'rate_c', 'tap', 'shift', 'br_status',
                            'angmin', 'angmax']
            if any([gen.extended for gen in self.dcline]):
                header_names += ['pf', 'qf', 'pt', 'qt', 'mu_sf', 'mu_st',
                                 'mu_angmin', 'mu_angmax']
            matpower_lines.append('%\t'+'\t'.join(header_names))
            matpower_lines.append('mpc.dcline = [')
            for dcline in self.dcline:
                matpower_lines.append('\t'+dcline.to_matpower()+';')
            matpower_lines.append('];')

        if self.dclinecost is not None:
            matpower_lines.append('')
            matpower_lines.append('%% dcline cost data')
            header_names = ['1', 'startup', 'shutdown', 'ncost', ' x_1',
                            'y_1', '...', 'x_ncost', 'y_ncost']
            matpower_lines.append('%\t'+'\t'.join(header_names))
            header_names = ['2', 'startup', 'shutdown', 'ncost',
                            ' c_(ncost-1)', '...', 'c_0']
            matpower_lines.append('%\t'+'\t'.join(header_names))
            matpower_lines.append('mpc.dclinecost = [')
            for dclinecost in self.dclinecost:
                matpower_lines.append('\t'+dclinecost.to_matpower()+';')
            matpower_lines.append('];')

        if self.busname is not None:
            matpower_lines.append('')
            matpower_lines.append('%% bus name data')
            header_names = ['name']
            matpower_lines.append('%\t'+'\t'.join(header_names))
            matpower_lines.append('mpc.bus_name = {')
            for busname in self.busname:
                matpower_lines.append('\t'+busname.to_matpower()+';')
            matpower_lines.append('};')

        matpower_lines.append('')

        return '\n'.join(matpower_lines)


    def remove_status_zero(self):
        bus = [copy.deepcopy(x) for x in self.bus]
        off_gen = [i for i, x in enumerate(self.gen) if x.status == 0]
        on_gen = [i for i, x in enumerate(self.gen) if x.status == 1]

        if len(off_gen) > 0:
            print("INFO: removing turned off gens: %s" % str(off_gen))
            gen = [copy.deepcopy(self.gen[i]) for i in on_gen]
            gencost = [copy.deepcopy(self.gencost[i]) for i in on_gen]
        else:
            gen = [copy.deepcopy(x) for x in self.gen]
            gencost = [copy.deepcopy(x) for x in self.gencost]

        off_branch = [i for i, x in enumerate(self.branch) if x.status == 0]
        on_branch = [i for i, x in enumerate(self.branch) if x.status == 1]

        if len(off_branch) > 0:
            print("INFO: removing turned off lines: %s" % str(off_branch))
            branch = [copy.deepcopy(self.branch[i]) for i in on_branch]
        else:
            branch = [copy.deepcopy(x) for x in self.branch]

        return Case(self.name+'_status-1', self.baseMVA, bus, gen, branch,
            gencost)


class Generator(object):
    def __init__(self, index, gen_bus, pg, qg, qmax, qmin, vg, mbase,
                 gen_status, pmax, pmin, pc1=0, pc2=0, qc1min=0, qc1max=0,
                 qc2min=0, qc2max=0, ramp_agc=0, ramp_10=0, ramp_30=0,
                 ramp_q=0, apf=0, mu_pmax=None, mu_pmin=None, mu_qmax=None,
                 mu_qmin=None):
        '''This data structure contains key power generator parameters.
        Some arguments have default values of 0 for backward compatibility
        with an older data specification.

        Args:
            index (int): unique generator identifier
            gen_bus (int): the identifier of the bus that this generator is
                connected to
            pg (float): active power output (MW)
            qg (float): reactive power output (MVAr)
            qmax (float): reactive power output upper bound (MVAr)
            qmin (float): reactive power output lower bound (MVAr)
            vg (float): voltage magnitude setpoint (volts p.u.)
            mbase (float): machine mva base (MVA)
            gen_status (int): generator status (in service > 0, out of
                service <= 0)
            pmax (float): active power output upper bound (MW)
            pmin (float): active power output lower bound (MW)
            pc1 (float): PQ capability curve, active power lower bound (MW)
            pc2 (float): PQ capability curve, active power upper bound (MW)
            qc1min (float): reactive power output lower bound, at PC1 (MVAr)
            qc1max (float): reactive power output upper bound, at PC1 (MVAr)
            qc2min (float): reactive power output lower bound, at PC2 (MVAr)
            qc2max (float): reactive power output upper bound, at PC2 (MVAr)
            ramp_agc (float): AGC ramp rate (MW/min)
            ramp_10 (float): ramp rate for 10 minute reserves (MW)
            ramp_30 (float): ramp rate for 30 minute reserves (MW)
            ramp_q (float): ramp rate for reactive power (MVAr/min)
            apf (float): area participation factor
            mu_pmax (float, optional): KKT multiplier on active power output
                upper bound (u/MW)
            mu_pmin (float, optional): KKT multiplier on active power output
                lower bound (u/MW)
            mu_qmax (float, optional): KKT multiplier on reactive power output
                upper bound (u/MVAr)
            mu_qmin (float, optional): KKT multiplier on reactive power output
                lower bound (u/MVAr)
        '''
        self.index = int(index)
        self.gen_bus = int(gen_bus)
        self.pg = float(pg)
        self.qg = float(qg)
        self.qmax = float(qmax)
        self.qmin = float(qmin)
        self.vg = float(vg)
        self.mbase = float(mbase)
        self.gen_status = int(gen_status)
        self.pmax = float(pmax)
        self.pmin = float(pmin)
        self.pc1 = float(pc1)
        self.pc2 = float(pc2)
        self.qc1min = float(qc1min)
        self.qc1max = float(qc1max)
        self.qc2min = float(qc2min)
        self.qc2max = float(qc2max)
        self.ramp_agc = float(ramp_agc)
        self.ramp_10 = float(ramp_10)
        self.ramp_30 = float(ramp_30)
        self.ramp_q = float(ramp_q)
        self.apf = float(apf)

        self.mu_pmax = _guard_none(float, mu_pmax)
        self.mu_pmin = _guard_none(float, mu_pmin)
        self.mu_qmax = _guard_none(float, mu_qmax)
        self.mu_qmin = _guard_none(float, mu_qmin)

        self.extended = any([x is not None
                             for x in [self.mu_pmax, self.mu_pmin,
                                       self.mu_qmax, self.mu_qmin]])

    def __str__(self):
        data = [self.index, self.gen_bus, self.pg, self.qg, self.qmax,
                self.qmin, self.vg, self.mbase, self.gen_status, self.pmax,
                self.pmin,
                self.pc1, self.pc2, self.qc1min, self.qc1max, self.qc2min,
                self.qc2max,
                self.ramp_agc, self.ramp_10, self.ramp_30, self.ramp_q,
                self.apf,
                self.mu_pmax, self.mu_pmin, self.mu_qmax, self.mu_qmin,
                self.extended]
        return ' '.join([str(x) for x in data])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def validate(self):
        '''Checks that this data structure conforms to the Matpower data
        specification
        '''
        pass

    def to_matpower(self):
        '''Returns: a Matpower encoding of this data structure as a string'''

        data = [self.gen_bus, self.pg, self.qg, self.qmax, self.qmin, self.vg,
                self.mbase, self.gen_status, self.pmax, self.pmin,
                self.pc1, self.pc2, self.qc1min, self.qc1max, self.qc2min,
                self.qc2max,
                self.ramp_agc, self.ramp_10, self.ramp_30, self.ramp_q,
                self.apf]

        if self.extended:
            data += [self.mu_pmax, self.mu_pmin, self.mu_qmax, self.mu_qmin]

        return '\t '.join([str(x) for x in data])


class MatpowerCost(object):
    def __init__(self, index, model, startup=0, shutdown=0, ncost=0, cost=[]):
        '''This data structure contains key power generator cost model
        parameters.  Note that the generator cost identifier (i.e. index) is
        used to link the cost model to a particular generator

        The piecewise linear model :math:`f(x)` is defined by,
        the coordinates :math:`(\\boldsymbol {cost}_0, \\boldsymbol {cost}_1)`,
        :math:`(\\boldsymbol {cost}_2, \\boldsymbol {cost}_3)`, 
        :math:`\\dots` , 
        :math:`(\\boldsymbol {cost}_{2 \\boldsymbol {ncost} - 1}, 
        \\boldsymbol {cost}_{2 \\boldsymbol {ncost}})` of the end/break-points 
        of the piecewise linear cost.

        The polynomial cost model is defined as,
        :math:`f(x) = \\sum_{i \\in 1 .. \\boldsymbol {ncost}} \\boldsymbol {cost}_{i-1} x^{\\boldsymbol {ncost} - i}`.

        Args:
            index (int): unique generator cost identifier
            model (int): generator cost model (piecewise linear = 1,
                polynomial = 2)
            startup (float): startup costs (US Dollars)
            shutdown (float): shutdown costs (US Dollars)
            ncost (int): number of data points or cost coefficients
            cost (list of float): the list of data points or cost coefficients
                (US Dollars/hour),
                if a polynomial model it should have ncost values,
                if a piecewise linear model it should have 2*ncost values
        '''

        self.index = int(index)
        self.model = int(model)
        self.startup = float(startup)
        self.shutdown = float(shutdown)
        self.ncost = int(ncost)
        self.cost = [float(x) for x in cost]
        # print self.costs

    def __str__(self):
        data = [self.index, self.model, self.startup, self.shutdown,
                self.ncost] + self.cost
        return ' '.join([str(x) for x in data])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def validate(self):
        '''Checks that this data structure conforms to the Matpower data
        specification
        '''

        if self.model in [1, 2]:
            if self.model == 1:
                if 2*self.ncost == len(self.cost):
                    if len(self.cost) > 0:
                        for i in range(self.ncost-1):
                            if not self.cost[i*2] < self.cost[i*2+2]:
                                warnings.warn('The piecewise linear x values '
                                    'in model %d are not strictly increasing.  '
                                    'See the points %s, %s' %
                                    (self.index,
                                      (self.cost[i*2], self.cost[i*2+1]),
                                      (self.cost[i*2+2], self.cost[i*2+3])),
                                    MPDataWarning)
                else:
                    warnings.warn('piecewise linear generator cost data %d '
                        'specified %d data points but %f coordinate '
                        'pairs were provided.' %
                        (self.index, self.ncost, len(self.cost)/2.0),
                        MPDataWarning)
            if self.model == 2 and self.ncost != len(self.cost):
                warnings.warn('polynomial generator cost data %d specified %d '
                    'cost coefficients but %d coefficients were provided.' %
                    (self.index, self.ncost, len(self.cost)), MPDataWarning)
        else:
            warnings.warn('generator cost data %d has an undefined model '
                'value of %d.  Only the values 1 and 2 are defined in the '
                'data specification.' % (self.index, self.model), 
                MPDataWarning)

    def to_matpower(self):
        '''Returns: a Matpower encoding of this data structure as a string'''

        data = [self.model, self.startup, self.shutdown, self.ncost] + \
            self.cost
        return '\t '.join([str(x) for x in data])

class GeneratorCost(MatpowerCost):
    pass

class DCLineCost(MatpowerCost):
    pass


class Bus(object):
    def __init__(self, bus_i, bus_type, pd, qd, gs, bs, area, vm, va, base_kv,
                 zone, vmax, vmin, lam_p=None, lam_q=None, mu_vmax=None,
                 mu_vmin=None):
        '''This data structure contains key power network bus parameters.

        Args:
            bus_i (int): unique bus identifier
            bus_type (int): PQ = 1, PV = 2, reference = 3, disconnected = 4
            pd (float): active power demand (MW)
            qd (float): reactive power demand (MVAr)
            gs (float): shunt conductance (MW at 1.0 volts p.u.)
            bs (float): shunt susceptance (MVAr at 1.0 volts p.u.)
            area (int): area identifier
            vm (float): voltage magnitude (volts p.u.)
            va (float): voltage angle (degrees)
            base_kv (float): base voltage (kilovolts)
            zone (int): loss zone
            vmax (float): voltage magnitude upper bound (volts p.u.)
            vmin (float): voltage magnitude lower bound (volts p.u.)
            lam_p (float, optional): Lagrange multiplier on active power KCL
                (u/MW)
            lam_q (float, optional): Lagrange multiplier on reactive power KCL
                (u/MVAr)
            mu_vmax (float, optional): KKT multiplier on voltage upper bound
                (u/volts p.u.)
            mu_vmin (float, optional): KKT multiplier on voltage lower bound
                (u/volts p.u.)
        '''

        self.bus_i = int(bus_i)
        self.bus_type = int(bus_type)
        self.pd = float(pd)
        self.qd = float(qd)
        self.gs = float(gs)
        self.bs = float(bs)
        self.area = int(area)
        self.vm = float(vm)
        self.va = float(va)
        self.base_kv = float(base_kv)
        self.zone = int(zone)
        self.vmax = float(vmax)
        self.vmin = float(vmin)

        self.lam_p = _guard_none(float, lam_p)
        self.lam_q = _guard_none(float, lam_q)
        self.mu_vmax = _guard_none(float, mu_vmax)
        self.mu_vmin = _guard_none(float, mu_vmin)

        self.extended = any([x is not None for x in [self.lam_p, self.lam_q,
                             self.mu_vmax, self.mu_vmin]])

    def __str__(self):
        data = [self.bus_i, self.bus_type, self.pd, self.qd, self.gs, self.bs,
                self.area, self.vm, self.va, self.base_kv,
                self.zone, self.vmax, self.vmin, self.lam_p,
                self.lam_q, self.mu_vmax, self.mu_vmin, self.extended]
        return ' '.join([str(x) for x in data])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def validate(self):
        '''Checks that this data structure conforms to the Matpower data
        specification
        '''

        if not self.bus_i >= 0:
            warnings.warn('bus %d has a negative identification number.  '
                'The data specification requires positive values.' %
                          (self.bus_i), MPDataWarning)

        if not self.area >= 0:
            warnings.warn('bus %d has a negative area number %d.  '
                'The data specification requires positive values.' %
                          (self.bus_i, self.area), MPDataWarning)

        if not self.zone >= 0:
            warnings.warn('bus %d has a negative zone number %d.  '
                'The data specification requires positive values.' %
                          (self.bus_i, self.zone), MPDataWarning)

        if self.bus_type not in [1, 2, 3, 4]:
            warnings.warn('bus %d has an undefined type value of %d.  '
                'Only the values 1, 2, 3, and 4 are defined in the data '
                'specification.' % (self.bus_i, self.bus_type), MPDataWarning)

    def to_matpower(self):
        '''Returns: a Matpower encoding of this data structure as a string'''

        data = [self.bus_i, self.bus_type, self.pd, self.qd, self.gs, self.bs,
                self.area, self.vm, self.va, self.base_kv,
                self.zone, self.vmax, self.vmin]

        if self.extended:
            data += [self.lam_p, self.lam_q, self.mu_vmax, self.mu_vmin]

        return '\t '.join([str(x) for x in data])


class BusName(object):
    def __init__(self, index, name):
        '''This data structure contains bus name parameters.

        Args:
            index (int): unique identifier for this bus name
            name (str): a bus name
        '''

        self.index = int(index)
        self.name = str(name)

    def __str__(self):
        data = [self.index, self.name]
        return ' '.join([str(x) for x in data])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def validate(self):
        '''Checks that this data structure conforms to the Matpower data
        specification
        '''
        pass

    def to_matpower(self):
        '''Returns: a Matpower encoding of this data structure as a string'''
        return '\'%s\'' % self.name



class Branch(object):
    def __init__(self, index, f_bus, t_bus, br_r, br_x, br_b=0.0, rate_a=0.0, rate_b=0.0,
                 rate_c=0.0, tap=0.0, shift=0.0, br_status=1, angmin=-360.0, angmax=360.0,
                 pf=None, qf=None, pt=None, qt=None, mu_sf=None, mu_st=None,
                 mu_angmin=None, mu_angmax=None):
        '''This data structure contains key power network branch parameters.
        If the value of tap or shift are non-zero, the branch is considered a
        transformer.  Angle difference bound arguments have default values for
        backward compatibility with an older data specification.

        Args:
            index (int): unique branch identifier
            f_bus (int): the identifier of the from bus
            t_bus (int): the identifier of the to bus
            br_r (float): the branch resistance (p.u.)
            br_x (float): the branch reactance (p.u.)
            br_b (float): the total branch charging susceptance (p.u.)
            rate_a (float): long term rating (MVA)
            rate_b (float): short term rating (MVA)
            rate_c (float): emergency rating (MVA)
            tap (float): transformer off nominal turn ratio (p.u.)
            shift (float): positive delay transformer phase shift (degrees)
            br_status (int): branch status (in service = 1, out of service = 0)
            angmin (float): phase angle difference lower bound (degrees)
            angmax (float): phase angle difference upper bound (degrees)
            pf (float, optional): from bus active power flow (MW)
            qf (float, optional): from bus reactive power flow (MVAr)
            pt (float, optional): to bus active power flow (MW)
            qt (float, optional): to bus reactive power flow (MVAr)
            mu_sf (float, optional): KKT multiplier on from bus long term
                rating limit (u/MVA)
            mu_st (float, optional): KKT multiplier on to bus long term rating
                limit (u/MVA)
            mu_angmin (float, optional): KKT multiplier on phase angle
                difference lower bound (u/degree)
            mu_angmax (float, optional): KKT multiplier on phase angle
                difference upper bound (u/degree)
        '''

        self.index = int(index)
        self.f_bus = int(f_bus)
        self.t_bus = int(t_bus)
        self.br_r = float(br_r)
        self.br_x = float(br_x)
        self.br_b = float(br_b)
        self.rate_a = float(rate_a)
        self.rate_b = float(rate_b)
        self.rate_c = float(rate_c)
        self.tap = float(tap)
        self.shift = float(shift)
        self.br_status = int(br_status)
        self.angmin = float(angmin)
        self.angmax = float(angmax)

        self.pf = _guard_none(float, pf)
        self.qf = _guard_none(float, qf)
        self.pt = _guard_none(float, pt)
        self.qt = _guard_none(float, qt)
        self.mu_sf = _guard_none(float, mu_sf)
        self.mu_st = _guard_none(float, mu_st)
        self.mu_angmin = _guard_none(float, mu_angmin)
        self.mu_angmax = _guard_none(float, mu_angmax)

        self.extended = any([x is not None for x in
            [self.pf, self.qf, self.pt, self.qt]])

        self.duals = any([x is not None for x in
            [self.mu_sf, self.mu_st, self.mu_angmin, self.mu_angmax]])

    def __str__(self):
        data = [self.index, self.f_bus, self.t_bus, self.br_r, self.br_x,
                self.br_b, self.rate_a, self.rate_b, self.rate_c,
                self.tap, self.shift, self.br_status, self.angmin, self.angmax,
                self.pf, self.qf, self.pt, self.qt, self.mu_sf, self.mu_st,
                self.mu_angmin, self.mu_angmax, self.extended, self.duals]
        return ' '.join([str(x) for x in data])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def validate(self):
        '''Checks that this data structure conforms to the Matpower data
        specification
        '''

        if self.br_status not in [0, 1]:
            warnings.warn('branch %d from bus %d to bus %d has a br_status '
                'value of of %d.  Only the values 0 and 1 are defined in the '
                'data specification.' %
                         (self.index, self.f_bus, self.t_bus, self.br_status),
                         MPDataWarning)

    def to_matpower(self):
        '''Returns: a Matpower encoding of this data structure as a string'''

        data = [self.f_bus, self.t_bus, self.br_r, self.br_x, self.br_b,
                self.rate_a, self.rate_b, self.rate_c,
                self.tap, self.shift, self.br_status, self.angmin, self.angmax]

        if self.extended:
            data += [self.pf, self.qf, self.pt, self.qt]

        if self.duals:
            data += [self.mu_sf, self.mu_st, self.mu_angmin, self.mu_angmax]

        return '\t '.join([str(x) for x in data])


class DCLine(object):
    def __init__(self, index, f_bus, t_bus, br_status, pf, pt, qf, qt, vf, vt,
                 pmin, pmax, qminf, qmaxf, qmint, qmaxt, loss0, loss1,
                 mu_pmin=None, mu_pmax=None, mu_qminf=None, mu_qmaxf=None,
                 mu_qmint=None, mu_qmaxt=None):
        '''This data structure contains key power network dc line parameters.

        Args:
            index (int): unique dc line identifier
            f_bus (int): the identifier of the from bus
            t_bus (int): the identifier of the to bus
            br_status (int): dc line status (in service = 1,
                out of service = 0)
            pf (float): from bus active power flow (MW)
            pt (float): to bus active power flow (MW)
            qf (float): from bus reactive power flow (MVAr)
            qt (float): to bus reactive power flow (MVAr)
            vf (float): from bus voltage magnitude setpoint (volts p.u.)
            vt (float): to bus voltage magnitude setpoint (volts p.u.)
            pmin (float): active power flow lower bound (MW), from bus if >= 0,
                to bus if < 0
            pmax (float): active power flow upper bound (MW), from bus if >= 0,
                to bus if < 0
            qminf (float): from bus reactive power flow lower bound (MVAr)
            qmaxf (float): from bus reactive power flow upper bound (MVAr)
            qmint (float): to bus reactive power flow lower bound (MVAr)
            qmaxt (float): to bus reactive power flow upper bound (MVAr)
            loss0 (float): constant term in from bus active power loss function
                (MW)
            loss1 (float): linear term in from bus active power loss function
                (scalar)
            mu_pmin (float, optional): KKT multiplier on from bus active power
                lower bound (u/MW)
            mu_pmax (float, optional): KKT multiplier on from bus active power
                upper bound (u/MW)
            mu_qminf (float, optional): KKT multiplier on from bus reactive
                power lower bound (u/MVAr)
            mu_qmaxf (float, optional): KKT multiplier on from bus reactive
                power upper bound (u/MVAr)
            mu_qmint (float, optional): KKT multiplier on to bus reactive
                power lower bound (u/MVAr)
            mu_qmaxt (float, optional): KKT multiplier on to bus reactive
                power upper bound (u/MVAr)
        '''

        self.index = int(index)
        self.f_bus = int(f_bus)
        self.t_bus = int(t_bus)
        self.br_status = int(br_status)
        self.pf = float(pf)
        self.pt = float(pt)
        self.qf = float(qf)
        self.qt = float(qt)
        self.vf = float(vf)
        self.vt = float(vt)
        self.pmin = float(pmin)
        self.pmax = float(pmax)
        self.qminf = float(qminf)
        self.qmaxf = float(qmaxf)
        self.qmint = float(qmint)
        self.qmaxt = float(qmaxt)
        self.loss0 = float(loss0)
        self.loss1 = float(loss1)

        self.mu_pmin = _guard_none(float, mu_pmin)
        self.mu_pmax = _guard_none(float, mu_pmax)
        self.mu_qminf = _guard_none(float, mu_qminf)
        self.mu_qmaxf = _guard_none(float, mu_qmaxf)
        self.mu_qmint = _guard_none(float, mu_qmint)
        self.mu_qmaxt = _guard_none(float, mu_qmaxt)

        self.extended = any([x is not None for x in [self.mu_pmin,
            self.mu_pmax, self.mu_qminf, self.mu_qmaxf, self.mu_qmint,
            self.mu_qmaxt]])

    def __str__(self):
        data = [self.index, self.f_bus, self.t_bus, self.br_status, self.pf,
                self.pt, self.qf, self.qt, self.vf, self.vt,
                self.pmin, self.pmax, self.qminf, self.qmaxf, self.qmint,
                self.qmaxt, self.loss0, self.loss1,
                self.mu_pmin, self.mu_pmax, self.mu_qminf, self.mu_qmaxf,
                self.mu_qmint, self.mu_qmaxt]
        return ' '.join([str(x) for x in data])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def validate(self):
        '''Checks that this data structure conforms to the Matpower data
        specification
        '''

        if self.br_status not in [0, 1]:
            warnings.warn('dc line %d from bus %d to bus %d has a br_status '
                'value of of %d.  Only the values 0 and 1 are defined in the '
                'data specification.' %
                (self.index, self.f_bus, self.t_bus, self.br_status),
                MPDataWarning)

    def to_matpower(self):
        '''Returns: a Matpower encoding of this data structure as a string'''

        data = [self.f_bus, self.t_bus, self.br_status, self.pf, self.pt,
                self.qf, self.qt, self.vf, self.vt,
                self.pmin, self.pmax, self.qminf, self.qmaxf, self.qmint,
                self.qmaxt, self.loss0, self.loss1]

        if self.extended:
            data += [self.mu_pmin, self.mu_pmax, self.mu_qminf, self.mu_qmaxf,
                     self.mu_qmint, self.mu_qmaxt]

        return '\t '.join([str(x) for x in data])

