/* Modern rewrite: ES Modules, fetch API, no jQuery */

document.addEventListener('DOMContentLoaded', () => {
    const accountsEl = document.getElementById('accounts');
    const addBtn = document.getElementById('add-account');
    const submitBtn = document.getElementById('submit-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const form = document.getElementById('config-form');
    const toastEl = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastOk = document.getElementById('toast-ok');

    let activeUin = '';

    async function apiGet(path, params = {}){
        const url = new URL(path, window.location.href);
        Object.keys(params).forEach(k => url.searchParams.append(k, params[k]));
        const res = await fetch(url);
        return res.json();
    }

    function clearForm(){
        form.reset();
    }

    function showToast(message){
        return new Promise(resolve => {
            toastMessage.textContent = message;
            toastEl.classList.remove('hidden');
            toastEl.setAttribute('aria-hidden', 'false');
            toastOk.focus();
            function onClose(){
                toastEl.classList.add('hidden');
                toastEl.setAttribute('aria-hidden', 'true');
                toastOk.removeEventListener('click', onClose);
                resolve();
            }
            toastOk.addEventListener('click', onClose);
        });
    }

    function setActiveLi(li){
        const prev = accountsEl.querySelector('.active');
        if(prev) prev.classList.remove('active');
        if(li) li.classList.add('active');
    }

    function makeLi(uin, isNew=false){
        const li = document.createElement('li');
        li.textContent = String(uin);
        li.tabIndex = 0;
        if(isNew) li.classList.add('newadd');
        li.addEventListener('click', () => selectAccount(uin, li));
        li.addEventListener('keypress', (e) => { if(e.key === 'Enter') selectAccount(uin, li); });
        return li;
    }

    async function loadAccounts(){
        try{
            const result = await apiGet('query_reply_list');
            if(result && result.result === 'success'){
                accountsEl.innerHTML = '';
                result.data.forEach(uid => accountsEl.appendChild(makeLi(uid)));
            }
        }catch(err){ console.error(err); }
    }

    async function selectAccount(uin, li){
        setActiveLi(li);
        activeUin = String(uin);
        clearForm();
        try{
            const result = await apiGet('query_reply', { uin: uin });
            if(result && result.result === 'success'){
                // map returned keys to form fields - maintain compatibility
                if(result.data.blocker_type !== undefined) form.querySelector('[name="blocker_type"]').value = String(result.data.blocker_type);
                if(result.data.command_on !== undefined) form.querySelector('[name="command_on"]').value = String(result.data.command_on);
                if(result.data.command_off !== undefined) form.querySelector('[name="command_off"]').value = String(result.data.command_off);
                if(result.data.reply_on){
                    form.querySelector('[name="reply_on_type"]').value = result.data.reply_on.type || 'text';
                    form.querySelector('[name="reply_on_data"]').value = result.data.reply_on.data || '';
                }
                if(result.data.reply_off){
                    form.querySelector('[name="reply_off_type"]').value = result.data.reply_off.type || 'text';
                    form.querySelector('[name="reply_off_data"]').value = result.data.reply_off.data || '';
                }
            }
        }catch(err){ console.error(err); }
    }

    addBtn.addEventListener('click', async () => {
        const uin = prompt('请输入要添加的账号 UIN（仅限数字）');
        if(!uin) return;
        if(!/^\d+$/.test(uin)){
            await showToast('UIN 必须为纯数字字符串');
            return;
        }
        const li = makeLi(uin, true);
        accountsEl.prepend(li);
        setActiveLi(li);
        activeUin = String(uin);
        clearForm();
    });

    submitBtn.addEventListener('click', async () => {
        if(!activeUin){ await showToast('您还没有选择或添加账号'); return; }
        const payload = {
            blocker_type: form.querySelector('[name="blocker_type"]').value,
            command_on: form.querySelector('[name="command_on"]').value,
            command_off: form.querySelector('[name="command_off"]').value,
            reply_on: {
                type: form.querySelector('[name="reply_on_type"]').value,
                data: form.querySelector('[name="reply_on_data"]').value
            },
            reply_off: {
                type: form.querySelector('[name="reply_off_type"]').value,
                data: form.querySelector('[name="reply_off_data"]').value
            }
        };

        try{
            const res = await fetch(`submit/${activeUin}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await res.json();
            if(result && result.result === 'success'){
                await showToast('修改/增加配置成功');
                const activeLi = accountsEl.querySelector('.active');
                if(activeLi && activeLi.classList.contains('newadd')) activeLi.classList.remove('newadd');
            }else{
                await showToast('修改/增加配置失败');
            }
        }catch(err){ console.error(err); alert('提交失败'); }
    });

    deleteBtn.addEventListener('click', async () => {
        if(!activeUin){ await showToast('您还没有选择或添加账号'); return; }
        if(!confirm('您确定要删除该配置吗')) return;
        const activeLi = accountsEl.querySelector('.active');
        if(activeLi && activeLi.classList.contains('newadd')){
            activeLi.remove(); clearForm(); activeUin = '';
            await showToast('删除配置成功');
            return;
        }
        try{
            const result = await apiGet('delete', { uin: activeUin });
            if(result && result.result === 'success'){
                if(activeLi) activeLi.remove();
                clearForm(); activeUin = '';
                await showToast('删除配置成功');
            }else{
                await showToast('删除配置失败');
            }
        }catch(err){ console.error(err); alert('删除请求失败'); }
    });

    // initial load
    loadAccounts();
});