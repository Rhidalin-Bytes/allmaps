#All maps plugin
#cmd is !maps or !maps low, !maps med, !maps high, !maps all

__version__ = '1.0'
__author__  = 'Rhidalin_Bytes'

import b3, re, string
import b3.events

class AllmapsPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    population = {'low':'sv_mapRotation_low','med':'sv_mapRotation_medium','high':'sv_mapRotation_high'}
    
    def startup(self):
        """\
        Initialize plugin settings
        """
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return False
    
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = self.getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)
        
        self.debug('Allmaps Started')


    def getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func

        return None

    def cmd_maps(self, data, client=None, cmd=None):
        """\
        <rotation> - For current rotation enter nothing or low, med, high or all for others.
        """

        if not self._adminPlugin.aquireCmdLock(cmd, client, 60, True):
            client.message('^7Do not spam commands')
            return

        if not data:
            maps = self.getMaps(self.rotation())
            data = "current"
        elif not data =='all':
            try:
                self.debug ('population = %s' % self.population[data])
                maps = self.getMaps(self.population[data])
            except:
                client.message('There was a problem getting %s' % self.population[data])
        else:
            try:
                maps = []
                for n in population:
                    self.debug ('population = %s' % self.population[n])
                    maps = maps + self.getMaps(self.population[n])
            except:
                client.message('There was a problem getting all maps')
        if maps:
            cmd.sayLoudOrPM(client, '^7Map Rotation(^2%s^7): ^2%s' % (data, string.join(maps, '^7, ^2')))
        else:
            client.message('You got no maps dummy')

    def cmd_nextmap(self, data, client=None, cmd=None):
        """\
        - list the next map in rotation
        """
        if not self._adminPlugin.aquireCmdLock(cmd, client, 60, True):
            client.message('^7Do not spam commands')
            return

        map = self.getNextMap()
        if map:
            cmd.sayLoudOrPM(client, '^7Next Map: ^2%s' % map)
        else:
            client.message('^7Error: could not get map list')
            
    _reMap = re.compile(r'map ([a-z0-9_-]+)', re.I)
    def getMaps(self, maploc='sv_mapRotation'):
        maps = self.console.getCvar(maploc)

        nmaps = []
        if maps:
            maps = re.findall(self._reMap, maps[0])

            for m in maps:
                if m[:3] == 'mp_':
                    m = m[3:]

                nmaps.append(m.title())

        return nmaps
    
    def getNextMap(self):
        if not self.console.game.mapName: return None
        
        maps = self.console.getCvar(self.rotation())

        if maps:
            maps = re.findall(self._reMap, maps[0])

            gmap = self.console.game.mapName.strip().lower()

            found = False
            for nmap in maps:
                nmap = nmap.strip().lower()
                if found:
                    found = nmap
                    break
                elif nmap == gmap:
                    # current map, break on next map
                    found = True

            if found == True:
                # map is first map in rotation
                nmap = maps[0].strip().lower()

            if found:
                if nmap[:3] == 'mp_': nmap = nmap[3:]
                return nmap.title()

            return None
        else:
            return None
            
    def rotation(self):
        cd = []
        rc = []
        i = []
        MRLB = self.console.getCvar('sv_mapRotationLoadBased')
        if MRLB.value is '1':
            rc = self.getMaps('sv_mapRotationCurrent')
            for n in self.population:
                cd = self.getMaps(self.population[n])
                i = list(set(rc) & set(cd))
                if i:
                    codmaps = self.population[n]
                    return codmaps
        else:
            codmaps = ('sv_mapRotation')
            self.debug('skipped loop')
            return codmaps
        
#_mrcs_sv_mapRotationCurrent_low " gametype sd map mp_bridge"
#_mrcs_sv_mapRotationCurrent_medium " gametype sd map mp_v2 gametype sd map mp_powcamp_n gametype sd map mp_ax_simmerath gametype sd map mp_kneedeep gametype sd map mp_trenchtoast gametype sd map mp_subway"
#_sl_current "medium"