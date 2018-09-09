import random
from vue import VueComponent, data, computed
from .widget import Widget
from browser import timer


class ProfileSelection(VueComponent):
    profiles = {
        "saw": {
            "settings": {
                "min": {"label": "Min"},
                "max": {"label": "Max"},
            }
        },
        "rand": {
            "settings": {
                "init": {"label": "Initial"},
                "var": {"label": "Variance"},
            }
        }
    }

    template = """
    <el-popover
        placement="right"
        width="200"
        v-model="visible"
        @hide="changed()"
    >
        <el-select
            v-model="name"
        >
            <el-option
                v-for="profile in Object.keys(profiles)"
                :key="profile"
                :label="profile"
                :value="profile"
            >
            </el-option>
        </el-select>
        <el-input-number
            v-for="e in Object.entries(profiles[name]['settings'])"
            :key="e[0]"
            size="mini"
            :controls="false"
            :placeholder="e[1]['label']"
            :label="e[1]['label']"
            :value="get(e[0])"
            @input="set(e[0], $event)"
        >
        </el-input-number>
        <el-button
            type="info" 
            size="mini"
            plain
            slot="reference"
        >
            {{ name }}
            <i class="el-icon-setting el-icon-right"></i>
        </el-button>
    </el-popover>
    """

    value: dict
    visible = False

    @computed
    def name(self):
        return self.settings.get("name", "saw")

    @name.setter
    def name(self, value):
        self.settings['name'] = value

    @data
    def settings(self):
        settings = {k: v for k, v in self.value.items()}
        return settings

    @computed
    def profile(self):
        profile = {k: self.settings[k]
                   for k in self.profiles[self.name]['settings'].keys()}
        profile['name'] = self.name

    def set(self, key, value):
        self.settings[key] = value

    def get(self, key):
        return self.settings.get(key, 0)

    def changed(self):
        self.emit("input", self.profile)


ProfileSelection.register()


class Generator(Widget):
    template_slots = """
    <el-table
        :data="profiles"
        size="mini"
        :border="true"
        style="width: 100%; height: 100%"
    >
        <el-table-column
            label="Topic"
        >
            <el-input 
                slot-scope="scope"
                size="mini"
                v-model="profiles[scope.$index]['topic']"
                @input="profile_changed(scope.$index)"
            >
            </el-input>
        </el-table-column>
        <el-table-column
            label="Profile"
            :width="100"
        >
            <profile-selection
                slot-scope="scope" 
                v-model="profiles[scope.$index]['settings']"
                @input="profile_changed(scope.$index)"
            >
            </profile-selection>
        </el-table-column>
        <el-table-column
            label="Frequency [ms]"
            :width="155"
        >
            <el-input-number 
                slot-scope="scope"
                size="mini"
                v-model="profiles[scope.$index]['frequency']"
                @input="profile_changed(scope.$index)"
                controls-position="right"
                :min="10"
                :max="10000"
                :step="100"
            >
            </el-input-number>
        </el-table-column>
        <el-table-column
            :width="35"
        >
            <el-checkbox
                slot-scope="scope"
                v-model="profiles[scope.$index]['enabled']"
                @input="profile_changed(scope.$index)"
            >
            </el-checkbox>
        </el-table-column>
        <el-table-column
            :width="50"
        >
            <el-button 
                slot-scope="scope"
                type="danger" 
                icon="el-icon-delete" 
                size="mini"
                @click="delete_profile(scope.$index)"
                circle>
            </el-button>
        </el-table-column>
        <div
            slot="append"
        >
            <el-button 
                type="success" 
                size="mini"
                @click="add_profile()"
                plain>
            New Profile
            </el-button>
        </div>
    </el-table>
    """

    has_settings = False

    @data
    def profiles(self):
        return self.get_prop("profiles")

    @computed
    def profiles_without_state(self):
        return [
            {k: v
             for k, v in profile.items()
             if k not in ['state']}
            for profile in self.profiles
        ]

    def adjust_height(self):
        self.set_height(13 + int(6.5 * len(self.profiles)))

    def created(self):
        for idx, _ in enumerate(self.profiles):
            self.profiles[idx]['state'] = {"timer": None, "value": None}
            self.reset_profile_state(idx)
        self.adjust_height()

    def delete_profile(self, idx):
        self.stop_timer(idx)
        del self.profiles[idx]
        self.adjust_height()

    def add_profile(self):
        self.profiles.append({'topic': '',
                              'frequency': 1000,
                              'enabled': False,
                              'settings': {'name': 'saw', "min": 0, "max": 100},
                              })
        self.reset_profile_state(len(self.profiles)-1)
        self.adjust_height()

    def reset_profile_state(self, idx):
        self.profiles[idx]['state'] = {"timer": None, "value": None}

    def profile_changed(self, idx):
        self.set_prop("profiles", self.profiles_without_state)
        self.profiles[idx]['state']['value'] = None
        self.restart_timer(idx)

    def stop_timer(self, idx):
        tmr = self.profiles[idx]['state']['timer']
        if tmr is not None:
            timer.clear_interval(tmr)

    def restart_timer(self, idx):
        self.stop_timer(idx)
        if self.profiles[idx]['enabled']:
            self.profiles[idx]['state']['timer'] = timer.set_interval(
                lambda: self.topic_update(idx),
                self.profiles[idx]['frequency']
            )

    def topic_update(self, idx):
        self.profiles[idx]['state']['value'] = self.calculate_updated_value(idx)
        self.mqtt.publish(self.profiles[idx]['topic'],
                          str(self.profiles[idx]['state']['value']))

    def calculate_updated_value(self, idx):
        settings = self.profiles[idx]['settings']
        old = self.profiles[idx]['state']['value']
        name = settings['name']
        if name == "saw":
            if old is None:
                return settings['min']
            return old + 1 if old < settings['max'] else settings['min']
        if name == "rand":
            if old is None:
                return settings['init']
            return old + random.randint(-settings['var'], settings['var'])
        return 0

    def destroyed(self):
        for idx, _ in enumerate(self.profiles):
            self.stop_timer(idx)


Generator.register("mdb-generator")
