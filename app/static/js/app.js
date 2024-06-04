new Vue({
    el: '#app',
    data() {
        return {
            options: [],
            treatment: '',
            outcome: '',
            common_causes: [],
            uploadFile: null,
            result: ''
        };
    },
    methods: {
        handleFileUpload(event) {
            this.uploadFile = event.target.files[0];
        },
        handleUpload() {
            const formData = new FormData();
            formData.append('file', this.uploadFile);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                this.options = data.columns.map(column => ({ value: column, label: column }));
            });
        },
        analyze() {
            const payload = {
                treatment: this.treatment,
                outcome: this.outcome,
                common_causes: this.common_causes
            };

            fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                this.result = data.message;
            });
        }
    },
    template: `
        <el-container>
            <el-header>
                <el-row class="top">
                    <el-col :span="2">
                        <input type="file" @change="handleFileUpload">
                        <el-button size="small" type="primary" @click="handleUpload">上传</el-button>
                    </el-col>
                    <el-col :span="4">
                        <el-select v-model="treatment" placeholder="Treatment">
                            <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="4">
                        <el-select v-model="outcome" placeholder="Outcome">
                            <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="4">
                        <el-select v-model="common_causes" placeholder="Common Causes" multiple>
                            <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value"></el-option>
                        </el-select>
                    </el-col>
                    <el-col :span="2">
                        <el-button type="primary" @click="analyze">确认</el-button>
                    </el-col>
                </el-row>
            </el-header>
            <el-main>
                <div class="content">
                    <el-input type="textarea" v-model="result" :autosize="{ minRows: 2, maxRows: 4}"></el-input>
                </div>
            </el-main>
        </el-container>
    `
    });